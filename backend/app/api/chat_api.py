from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ollama import Client
import asyncio
from functools import partial
from typing import Dict, List, Optional
import uuid
import logging
import traceback
import base64
import os
from app.service.tts_service import generate_chat_audio_file
import time
from pathlib import Path
from app.service.functioncall_service import call_function_service
from app.service.ollamachat_service import get_ollama_response
from app.configmanager import config
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ImageData(BaseModel):
    """图片数据模型"""
    base64_data: str
    file_name: str

class ChatRequest(BaseModel):
    ja_v1: bool = False
    tools_v1: bool
    message: str
    conversation_id: Optional[str] = None  # 可选的会话ID
    images: List[ImageData] = []  # 图片数据列表

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    audio_file_path: str

class ConversationStatus(BaseModel):
    conversation_id: str
    message_count: int
    last_message: str = None


# 存储对话历史
conversation_histories_normal: Dict[str, List[dict]] = {}
conversation_histories_ja: Dict[str, List[dict]] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天API端点
    """

        # 以键值对形式打印日志
    message_preview = request.message[:50] + "..." if len(request.message) > 50 else request.message
    logger.info("收到聊天请求 message: %r; tools_v1: %s; conversation_id: %s", 
                message_preview, 
                request.tools_v1, 
                request.conversation_id or "新会话")
                
    try:
        # 处理图片
        if request.images:
            BASE_DIR = Path(__file__).resolve().parent.parent.parent
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # 创建comfui/会话ID/input目录结构
            IMAGES_DIR = os.path.join(BASE_DIR, "comfui", conversation_id, "input")
            os.makedirs(IMAGES_DIR, exist_ok=True)
            
            saved_image_paths = []
            for img in request.images:
                try:
                    # 直接使用传入的文件名
                    image_filename = img.file_name  # 这里已经是"序号.后缀"格式
                    image_path = os.path.join(IMAGES_DIR, image_filename)
                    
                    # 解码并保存图片
                    image_data = img.base64_data
                    if ',' in image_data:
                        image_data = image_data.split(',')[1]
                    
                    with open(image_path, 'wb') as f:
                        f.write(base64.b64decode(image_data))
                    
                    saved_image_paths.append(image_path)
                    logger.info(f"图片已保存: {image_path}")
                
                except Exception as e:
                    logger.error(f"保存图片失败: {str(e)}")
                    raise e
        
        call_messages = []
        conversation_id = request.conversation_id or str(uuid.uuid4())
        logger.info("使用会话ID: %s", conversation_id)
        # 获取或初始化会话历史
        if request.ja_v1:
            if conversation_id not in conversation_histories_ja:
                conversation_histories_ja[conversation_id] = []
                logger.info("ja历史会话历史记录不存在，创建新会话集合: %s", conversation_id)
            call_messages = conversation_histories_ja[conversation_id]
           
        else:
            if conversation_id not in conversation_histories_normal:
                conversation_histories_normal[conversation_id] = []
                logger.info("normal会话历史记录不存在，创建新会话集合: %s", conversation_id)
            call_messages = conversation_histories_normal[conversation_id]
        
        

        if request.tools_v1:
        # 调用 functioncall_service
            response_content = call_function_service(request.message)
            response_content  = response_content["message"]
        else:   
            # 添加用户消息到历史记录
            message = {
                "role": "user",
                "content": request.message
            }
            chat_size = len(call_messages)
            model_name = config.ja_model if request.ja_v1 == True else config.normal_model
            logger.info(f"确定使用大模型: {model_name}, 当前会话历史大小: {chat_size}")
            model_name = config.ja_model if request.ja_v1 == True else config.normal_model
            call_messages.append(message)
            response_content = await get_ollama_response(
                    conversation_messages=call_messages,
                    model_name = model_name
                )
                

        BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 这会得到backend目录的绝对路径
        media_dir = os.path.join(BASE_DIR, "chat_media")
        # 使用会话ID和时间戳创建唯一文件名
        timestamp = int(time.time())
        audio_filename = f"{conversation_id}_{timestamp}.wav"
        audio_file_path = os.path.join(media_dir, audio_filename)  # 这是绝对路径

        
        # 调用TTS服务生成音频
        tts_success = generate_chat_audio_file(
            output_file_path=audio_file_path,
            text=response_content,
            text_language="ja" if request.ja_v1 else "zh"  # 根据ja_v1参数动态设置语言
        )
        
        if tts_success:
            logger.info(f"生成音频成功: {audio_file_path}")
            # 可以添加音频文件路径到返回结果中，如果前端需要
            audio_rel_path = os.path.join("chat_media", audio_filename)
        
        else:
            logger.error(f"生成音频失败")
            raise HTTPException(status_code=500, detail="生成音频失败")

        # 添加助手回复到历史记录
        assistant_message = {
            "role": "assistant",
            "content": response_content
        }
        if request.ja_v1:
            conversation_histories_ja[conversation_id].append(assistant_message)
        else:
            conversation_histories_normal[conversation_id].append(assistant_message)
                

        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id,
            audio_file_path = audio_rel_path
        )
        
    except Exception as e:

        error_msg = f"对话api执行出错: {str(e)}"
        error_stack = traceback.format_exc()
        # 使用logger记录详细错误信息
        logger.error(f"堆栈信息:\n{error_stack}")
        # logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/conversation/{conversation_id}", response_model=ConversationStatus)
async def get_conversation_status(conversation_id: str):
    """获取特定对话的状态"""
    if conversation_id not in conversation_histories:
        raise HTTPException(status_code=404, detail="未找到指定的对话")
    
    history = conversation_histories[conversation_id]
    last_message = history[-1]['content'] if history else None
    
    return ConversationStatus(
        conversation_id=conversation_id,
        message_count=len(history),
        last_message=last_message
    )

@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """清除指定的对话历史"""
    if conversation_id in conversation_histories:
        del conversation_histories[conversation_id]
        return {"message": "对话历史已清除"}
    raise HTTPException(status_code=404, detail="未找到指定的对话")

@router.get("/status")
async def get_ollama_status():
    """检查Ollama服务是否可用"""
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, ollama_client.list)
        return {"status": "online", "host": ollama_client.host}
    except Exception as e:
        return {"status": "offline", "error": str(e)}
