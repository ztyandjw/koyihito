import comfui_base_workflow
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ComfuiReactorSwapface(comfui_base_workflow.ComfuiBaseWorkflow):
    def comfui_workflow(self) -> str:
        return "reactor_swap_face"

    def build_payload(self, source_image: str, target_image: str, source_image_human_index: int, target_image_human_index: int) -> dict:
        """构建ReActor人脸交换的具体payload"""
        logger.info(f"构建ReActor人脸交换的payload - 源图片路径: {source_image}, 目标图片路径: {target_image}, 源图片人脸索引: {source_image_human_index}, 目标图片人脸索引: {target_image_human_index}")
        return {
            "client_id": self.client_id,
            "prompt": {
                "1": {
                    "inputs": {
                        "enabled": True,
                        "swap_model": "inswapper_128.onnx",
                        "facedetection": "retinaface_resnet50",
                        "face_restore_model": "codeformer-v0.1.0.pth",
                        "face_restore_visibility": 1,
                        "codeformer_weight": 1,
                        "detect_gender_input": "no",
                        "detect_gender_source": "no",
                        "input_faces_index": target_image_human_index,
                        "source_faces_index": source_image_human_index,
                        "console_log_level": 1,
                        "input_image": ["2", 0],
                        "source_image": ["3", 0]
                    },
                    "class_type": "ReActorFaceSwap",
                    "_meta": {"title": "ReActor 🌌 Fast Face Swap"}
                },
                "2": {
                    "inputs": {"image": target_image},
                    "class_type": "LoadImage",
                    "_meta": {"title": "加载图像"}
                },
                "3": {
                    "inputs": {"image": source_image},
                    "class_type": "LoadImage",
                    "_meta": {"title": "加载图像"}
                },
                "4": {
                    "inputs": {"images": ["1", 0]},
                    "class_type": "PreviewImage",
                    "_meta": {"title": "预览图像"}
                }
            },
            "extra_data": {
                "extra_pnginfo": {
                    "workflow": {
                        "last_node_id": 4,
                        "last_link_id": 3,
                        "nodes": [
                            # 节点配置...
                        ],
                        "links": [
                            [1, 2, 0, 1, 0, "IMAGE"],
                            [2, 3, 0, 1, 1, "IMAGE"],
                            [3, 1, 0, 4, 0, "IMAGE"]
                        ],
                        "version": 0.4
                    }
                }
            }
        }

if __name__ == "__main__":
    # 使用示例
    reactor_swapface = ComfuiReactorSwapface(
        server_address="http://127.0.0.1:8188",
        client_id="reactor_swapper_001"
    )
    
    target_img = "D:\\AI2025\\微信图片_20250313000526.jpg"
    source_img = "D:\\AI2025\\lss.jpg"
    
    try:
        logger.info("开始人脸交换", extra={'client_id': reactor_swapface.client_id})
        payload = reactor_swapface.build_payload(source_img, target_img, 0, 0)
        output_path = reactor_swapface.execute_workflow(payload)
        logger.info(f"处理完成: {output_path}", extra={'client_id': reactor_swapface.client_id})
    except Exception as e:
        logger.error(f"处理失败: {str(e)}", extra={'client_id': reactor_swapface.client_id})
