from typing import List, Dict
import asyncio
from functools import partial
import logging
from ollama import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Ollama client
ollama_client = Client(host="http://10.66.8.15:11434")

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
                model_name=model_name,
                stream=False
            )
        )
        content = response['message']['content'].strip()
        logger.info(f"Successfully called Ollama model {model_name}. Response: content")
        return content
    except Exception as e:
        logger.error(f"Error in get_ollama_response: {str(e)}")
        raise