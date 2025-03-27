from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ollama import Client
import asyncio
from functools import partial
from typing import Dict, List
import uuid
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 简化请求模型，只需要消息内容
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None  # 可选的会话ID

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class ConversationStatus(BaseModel):
    conversation_id: str
    message_count: int
    last_message: str = None

# 初始化 Ollama 客户端
ollama_client = Client(host="http://10.66.8.15:11434")

# 存储对话历史
conversation_histories: Dict[str, List[dict]] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ollama(request: ChatRequest):
    """
    聊天API端点
    """
    # 打印请求参数
    print(f"收到聊天请求: {request.dict()}")
    # await asyncio.sleep(10)

    try:
        # 检查是否有现有会话ID，没有则创建新的
        conversation_id = request.conversation_id or str(uuid.uuid4())
        print(f"使用会话ID: {conversation_id}")

        # 获取或初始化会话历史
        if conversation_id not in conversation_histories:
            conversation_histories[conversation_id] = []
            print(f"创建新会话: {conversation_id}")
        
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
        
        # 添加助手回复到历史记录
        assistant_message = {
            "role": "assistant",
            "content": response['message']['content']
        }
        conversation_histories[conversation_id].append(assistant_message)
        
        print(f"Ollama 响应: {response['message']['content'][:100]}...")
        
        return ChatResponse(
            response=response['message']['content'],
            conversation_id=conversation_id
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
