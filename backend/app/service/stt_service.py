import requests
import time
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def speech_to_text(audio_file_path, language="zh", model="medium"):
    """
    调用STT服务将语音转换为文本
    
    Args:
        audio_file_path: 音频文件的路径
        language: 音频的语言 (默认: 中文)
        model: 使用的模型 (默认: medium)
        
    Returns:
        tuple: (是否成功, 转换的文本或错误信息, 处理时间)
    """
    try:
        url = "http://10.66.8.15:9977/api"
        data = {
            "language": language,
            "model": model,
            "response_format": "txt"
        }
        
        # 打开音频文件
        with open(audio_file_path, "rb") as file:
            files = {"file": file}
            
            # 发送POST请求
            response = requests.post(url, data=data, files=files)
        
        
        # 处理响应
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"STT服务响应: {response_data}")
            
            # 提取文本 (根据您的示例，取最后一行文本)
            text = re.search(r'[^\n]+$', response_data["data"]).group()
            logger.info(f"STT文本内容:" + text)

            return True, text
        else:
            error_msg = f"STT请求失败，状态码: {response.status_code}，错误信息: {response.text}"
            logger.error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"STT服务调用出错: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

