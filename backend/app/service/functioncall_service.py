from ollama import Client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


import os

def create_folder_windows(args: dict):
    """
    在Windows系统指定路径下创建文件夹
    
    Args:
        args: 包含参数的字典
            - path: 要创建文件夹的路径
            - folder_name: 要创建的文件夹名称
        
    Returns:
        dict: 包含操作是否成功的信息
    """
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    try:
        path = args.get("path")
        folder_name = args.get("folder_name")
        print("11111" , path,folder_name)
        if not path or not folder_name:
            return {
                "success": False,
                "message": "缺少必要参数：path 或 folder_name"
            }
            
        # 组合完整路径
        full_path = os.path.join(path, folder_name)
        
    
            
        # 检查文件夹是否已存在
        if os.path.exists(full_path):
            return {
                "success": False,
                "message": f"文件夹已存在: {full_path}"
            }
            
        # 创建文件夹
        os.makedirs(full_path)
        return {
            "success": True,
            "message": f"主人您要求创建的文件夹成功了鸭"
        }
        
    except Exception as e:
        print(str(e))
        return {
            "success": False,
            "message": f"创建文件夹失败: {str(e)}"
        }

def call_function_service(user_message):
    print(user_message)
    try:
        ollama_host = "http://10.66.8.15:11434"
        client = Client(host=ollama_host)

        current_message = {
            "role": "user",
            "content":user_message
        }

        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "windows create file",
                    "description": "windows系统创建文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "文件名称"
                            }
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "windows_create_folder",
                    "description": "windows系统创建文件夹",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "folder_name": {
                                "type": "string",
                                "description": "文件夹名称"
                            },
                            "path": {
                                "type": "string",
                                "description": "创建文件夹的路径"
                            }
                        }
                    },
                    "required": ["path","folder_name"]
                }
            }
        ]
        conversation_history = []
        conversation_history.append({"role": "user", "content": user_message})
        
        response = client.chat(
        # model="TaterTot/susu",
        model="llama3-groq-tool-use",
        messages=conversation_history,
        stream=False,
        tools=tools,
    )
        print(response.message)
        # 将 arguments 转换为字典
        args = dict(response.message.tool_calls[0].function.arguments.items())
        print(args)
        print(response.message.tool_calls == None)
        # 检查是否存在 tool_calls
        if response.message.tool_calls is not None:
            success, result = create_folder_windows(args)
            return {
                "success": success,
                "message": result
            }
        else:
            print("没有工具调用")
            return {
                "success": False,
                "message": "我找了一圈，没有可用工具捏"
            }

    except Exception as e:
        print("6666666666666666" + str(e))
        return {
            "success": False,
            "message": str(e)
        }