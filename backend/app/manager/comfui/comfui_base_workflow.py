import requests
import time
import os
from typing import Dict, Any
import websocket
import json
import sys
import logging
from abc import ABC, abstractmethod

# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(client_id)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ComfuiBaseWorkflow(ABC):
    def __init__(self, server_address: str = "http://127.0.0.1:8188", client_id: str = "default_client"):
        self.server_address = server_address
        self.ws = None
        self.client_id = client_id
        self.is_processing = False
    @abstractmethod
    def comfui_workflow(self) -> str:
        return ""
    
    def connect_websocket(self):
        """连接WebSocket"""
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(f"ws://{self.server_address.split('://')[-1]}/ws?clientId={self.client_id}")
            logger.info("WebSocket连接成功", extra={'client_id': self.client_id})
        except Exception as e:
            logger.error(f"WebSocket连接失败: {str(e)}", extra={'client_id': self.client_id})
            raise

    def monitor_progress(self, prompt_id: str):
        """监控进度的主循环"""
        try:
            self.is_processing = True
            timeout = 0
            self.ws.settimeout(1.0)
            
            while self.is_processing and timeout < 300:
                try:
                    message = self.ws.recv()
                    if not message:
                        continue
                        
                    data = json.loads(message)
                    
                    if data.get("type") == "progress":
                        value = data.get("data", {}).get("value", 0)
                        max_value = data.get("data", {}).get("max", 1)
                        progress = (value / max_value * 100) if max_value > 0 else 0
                        print(f"\r当前处理进度: {progress:.1f}%", end="", flush=True)
                    
                    elif data.get("type") == "executed":
                        if data.get("data", {}).get("node") is None:
                            logger.info("处理完成", extra={'client_id': self.client_id})
                            self.is_processing = False
                            break
                    
                    elif data.get("type") == "execution_start":
                        logger.info("开始执行", extra={'client_id': self.client_id})
                        
                    elif data.get("type") == "execution_cached":
                        logger.info("处理完成", extra={'client_id': self.client_id})
                        time.sleep(3)
                        self.is_processing = False
                        break
                        
                    elif data.get("type") == "error":
                        logger.error(f"错误: {data.get('data', {}).get('message', '未知错误')}", 
                                   extra={'client_id': self.client_id})
                        self.is_processing = False
                        break
                
                except websocket.WebSocketTimeoutException:
                    history = self._get_history(prompt_id)
                    if prompt_id in history:
                        logger.info("处理完成", extra={'client_id': self.client_id})
                        self.is_processing = False
                        break
                    timeout += 1
                    continue
                    
        except Exception as e:
            logger.error(f"监控进度出错: {str(e)}", extra={'client_id': self.client_id})
            self.is_processing = False
            raise
        finally:
            self.is_processing = False


            
    @abstractmethod
    def build_payload(self, *args, **kwargs) -> Dict[str, Any]:
        """构建请求payload，可以接受任意参数"""
        pass
        
    
    def execute_workflow(self, payload: Dict[str, Any], output_dir: str = "output") -> str:
        """执行工作流并实时显示进度"""
        try:
            if not self.ws:
                self.connect_websocket()
            
            
            
            logger.info("提交工作流", extra={'client_id': self.client_id})
            prompt_id = self._queue_prompt(payload)
            
            self.monitor_progress(prompt_id)
            
            history = self._get_history(prompt_id)
            if prompt_id in history:
                image_path = self._get_output_image(history[prompt_id], output_dir)
                logger.info(f"结果已保存: {image_path}", extra={'client_id': self.client_id})
                return image_path
            
            raise Exception("处理失败，未找到结果")
            
        except Exception as e:
            logger.error(f"执行工作流出错: {str(e)}", extra={'client_id': self.client_id})
            raise
        finally:
            if self.ws:
                try:
                    self.ws.close()
                except:
                    pass

    def _queue_prompt(self, payload: Dict[str, Any]) -> str:
        """提交提示到ComfyUI"""
        response = requests.post(
            f"{self.server_address}/prompt",
            json=payload
        )
        response.raise_for_status()
        return response.json()["prompt_id"]
    
    def get_progress(self) -> float:
        """获取当前进度并返回百分比"""
        try:
            response = requests.get(f"{self.server_address}/progress")
            response.raise_for_status()
            data = response.json()
            progress = (data["value"] / data["max"]) * 100 if data["max"] > 0 else 0
            logger.info(f"当前进度: {progress:.1f}%", extra={'client_id': self.client_id})
            return progress
        except Exception as e:
            logger.error(f"获取进度出错: {str(e)}", extra={'client_id': self.client_id})
            return 0.0

    def wait_for_completion(self, prompt_id: str, poll_interval: float = 0.5) -> Dict[str, Any]:
        """等待工作流完成并显示进度"""
        while True:
            history = self._get_history(prompt_id)
            if prompt_id in history:
                logger.info("处理完成", extra={'client_id': self.client_id})
                return history[prompt_id]
            
            progress = self.get_progress()
            time.sleep(poll_interval)
    
    def _get_history(self, prompt_id: str) -> Dict[str, Any]:
        """获取执行历史"""
        response = requests.get(f"{self.server_address}/history/{prompt_id}")
        return response.json()

    def _get_output_image(self, result: Dict[str, Any], output_dir: str) -> str:
        """从结果中提取并保存输出图片"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 查找PreviewImage节点的输出
        last_preview_node = None
        for node_id, node_output in result["outputs"].items():
            if "images" in node_output:
                last_preview_node = node_output
        
        if last_preview_node is None:
            raise ValueError("未找到任何预览节点")
        
        # 获取该节点的最后一张图片
        images_list = last_preview_node["images"]
        if not images_list:
            raise ValueError("预览节点中没有图片")
        
        last_image = images_list[-1]
        filename = last_image["filename"]
        subfolder = last_image.get("subfolder", "")
        
        # 下载图片
        image_url = f"{self.server_address}/view?filename={filename}&type=temp"
        if subfolder:
            image_url += f"&subfolder={subfolder}"
        
        response = requests.get(image_url)
        response.raise_for_status()
        
        # 保存图片
        output_path = os.path.join(output_dir, filename)
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path
        
        raise ValueError("未找到输出图片")



if __name__ == "__main__":
    face_swapper = ComfuiManager(
        server_address="http://127.0.0.1:8188",
        client_id="custom_client_001"
    )
    input_img = "D:\\AI2025\\微信图片_20250313000526.jpg"
    source_img = "D:\\AI2025\\lss.jpg"
    
    try:
        logger.info("开始人脸交换", extra={'client_id': face_swapper.client_id})
        
        payload = face_swapper.build_payload(input_image, source_image)
        output_path = face_swapper.execute_workflow(input_img, source_img)
        logger.info(f"处理完成: {output_path}", extra={'client_id': face_swapper.client_id})
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", extra={'client_id': face_swapper.client_id})