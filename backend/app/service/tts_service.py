import requests
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_chat_audio_file(output_file_path, text, text_language="zh"):
    """
    Generate a WAV audio file from the provided text using TTS service
    
    Args:
        output_file_path: Full path where the WAV file will be saved
        text: The text to be converted to speech
        text_language: Language of the text (default: Chinese)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:

        logger.info(f"接收到的文本: {text}; 文本语言: {text_language}; 生成的录音文件路径: {output_file_path}")
        # Prepare the data for the TTS service
        data = {
            "text": text,
            "text_language": text_language
        }
        
        # Send the request to the TTS service
        response = requests.post("http://10.66.8.15:3111", json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Save the audio content to the specified file path
            with open(output_file_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            logger.error(f"TTS call failed: {response.content}")
            return False
            
    except Exception as e:
        logger.error(f"Error in generate_chat_audio_file: {str(e)}")
        raise e