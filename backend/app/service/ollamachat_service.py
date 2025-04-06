from typing import List, Dict
import asyncio
from functools import partial
import logging
from ollama import Client
from app.configmanager import config
from app.error import CustomError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Ollama client
ollama_client = Client(host=config.ollama_host)




def get_single_function_call(
    message: str,
    model_name: str,
    tools: List[Dict[str, object]],
):
    """
    """
    try:
        conversation_history = []
        conversation_history.append({"role": "user", "content": message})
        response = ollama_client.chat(
            messages=conversation_history,
            model=model_name,
            stream=False
        )
        if not response['message']['content']['tool_calls'] or len( response['message']['content']['tool_calls']) < 1:
            raise CustomError("No tool calls found in response")
        else:
            func_name = response['message']['content']['tool_calls'][0].function.name
            arguments = dict(response['message']['content']['tool_calls'][0].function.arguments.items())
            logger.info(f"called Func tools successfully: {func_name} {arguments}")
            return func_name, arguments
    except Exception as e:
        logger.error(f"called Func tools Failed: {str(e)}")
        raise CustomError(f"called Func tools Failed: {str(e)}")
 



async def get_ollama_response(
    conversation_messages: List[Dict[str, str]],
    model_name: str,
) -> str:
    """
    """
    try:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            partial(
                ollama_client.chat,
                messages=conversation_messages,
                model=model_name,
                stream=False
            )
        )
        content = response['message']['content'].strip()
        logger.info(f"Successfully called Ollama model {model_name}. Response: {content}")
        return content
    except Exception as e:
        logger.error(f"Error in get_ollama_response: {str(e)}")
        raise