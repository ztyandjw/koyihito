import requests


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
            print(f"TTS service returned error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error generating audio file: {str(e)}")
        return False