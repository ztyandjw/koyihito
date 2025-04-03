from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ollama import Client
import asyncio
from functools import partial
from typing import Dict, List
import uuid
import logging

from app.service.tts_service import generate_chat_audio_file
import os
import time
from pathlib import Path
from app.service.functioncall_service import call_function_service


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 简化请求模型，只需要消息内容
class ChatRequest(BaseModel):
    tools_v1: bool
    message: str
    conversation_id: str = None  # 可选的会话ID

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    audio_file_path: str = None

class ConversationStatus(BaseModel):
    conversation_id: str
    message_count: int
    last_message: str = None

# 初始化 Ollama 客户端
ollama_client = Client(host="http://10.66.8.15:11434")

# 存储对话历史
conversation_histories: Dict[str, List[dict]] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天API端点
    """

        # 以键值对形式打印日志
    message_preview = request.message[:50] + "..." if len(request.message) > 50 else request.message
    logger.info("收到聊天请求: message: %r, tools_v1: %s, conversation_id: %s", 
                message_preview, 
                request.tools_v1, 
                request.conversation_id or "新会话")
                
    # 打印请求参数
    print(f"收到聊天请求: {request.dict()}")
    # await asyncio.sleep(10)



    try:




        conversation_id = request.conversation_id or str(uuid.uuid4())
        print(f"使用会话ID: {conversation_id}")
         # 获取或初始化会话历史
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = []
            print(f"创建新会话: {conversation_id}")
        
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
            conversation_histories[conversation_id].append(message)
            
            # 打印当前会话的所有消息
            print(f"当前会话历史: {conversation_histories[conversation_id]}")
            
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                partial(
                    ollama_client.chat,
                    model="TaterTot/susu",
                    messages=conversation_histories[conversation_id],  # 发送完整的对话历史
                    stream=False
                )
            )
            # 获取Ollama响应内容
            response_content = response['message']['content']
        
        
        BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 这会得到backend目录的绝对路径
        media_dir = os.path.join(BASE_DIR, "chat_media")
        # 使用会话ID和时间戳创建唯一文件名
        timestamp = int(time.time())
        audio_filename = f"{conversation_id}_{timestamp}.wav"
        audio_file_path = os.path.join(media_dir, audio_filename)  # 这是绝对路径


        print("luyin: " +response_content)

        # 调用TTS服务生成音频
        tts_success = generate_chat_audio_file(
            output_file_path=audio_file_path,
            text=response_content,
            text_language="zh"  # 默认使用中文，可根据需要调整
        )
        
        if tts_success:
            logger.info(f"生成音频成功: {audio_file_path}")
            # 可以添加音频文件路径到返回结果中，如果前端需要
            audio_rel_path = os.path.join("chat_media", audio_filename)
        
        
        else:
            logger.error(f"生成音频失败")
            audio_rel_path = None
        
        # 添加助手回复到历史记录
        assistant_message = {
            "role": "assistant",
            "content": response_content
        }
        conversation_histories[conversation_id].append(assistant_message)
        
        print(f"Ollama 响应: {response_content[:100]}...")
        
        return ChatResponse(
            response=response_content,
            conversation_id=conversation_id,
            audio_file_path = audio_rel_path
        )
        
    except Exception as e:
        error_msg = f"处理请求时出错: {str(e)}"
        print(f"错误: {error_msg}")
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
