import requests
import os
import base64
import tempfile
import sys
import subprocess

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# Language code mapping
LANGUAGE_MAP = {
    "hi-IN": "hi-IN",  # Hindi
    "en-IN": "en-IN",  # English
    "bn-IN": "bn-IN",  # Bengali
    "kn-IN": "kn-IN",  # Kannada
    "ml-IN": "ml-IN",  # Malayalam
    "mr-IN": "mr-IN",  # Marathi
    "od-IN": "od-IN",  # Odia
    "pa-IN": "pa-IN",  # Punjabi
    "ta-IN": "ta-IN",  # Tamil
    "te-IN": "te-IN",  # Telugu
    "gu-IN": "gu-IN",  # Gujarati
}

def _guess_extension(audio_bytes):
    if len(audio_bytes) >= 4 and audio_bytes[:4] == b'RIFF':
        return '.wav'
    if len(audio_bytes) >= 3 and audio_bytes[:3] == b'ID3':
        return '.mp3'
    if len(audio_bytes) >= 1 and audio_bytes[0] == 0xFF:
        return '.mp3'
    return '.mp3'

def _autoplay_audio(audio_bytes):
    """Save to temp file and attempt to play automatically."""
    ext = _guess_extension(audio_bytes)
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tf:
        tf.write(audio_bytes)
        temp_path = tf.name

    # Try playsound if available
    try:
        from playsound import playsound
        playsound(temp_path)
        return temp_path
    except Exception:
        pass

    # On Windows, try winsound for WAV
    try:
        if sys.platform.startswith("win") and ext == '.wav':
            import winsound
            winsound.PlaySound(temp_path, winsound.SND_FILENAME)
            return temp_path
    except Exception:
        pass

    # Fallback: open with default app (Windows: os.startfile)
    try:
        if sys.platform.startswith("win"):
            os.startfile(temp_path)
        else:
            # cross-platform fallback
            subprocess.Popen(['start', temp_path], shell=True)
    except Exception:
        pass

    return temp_path

def text_to_speech(text, language_code="hi-IN", speaker="kavya", autoplay=True):
    """
    Convert text to speech using Sarvam AI
    
    Args:
        text: Text to convert to speech
        language_code: Language code (e.g., hi-IN, en-IN)
        speaker: Voice speaker name
        autoplay: If True, attempt to play audio automatically
    
    Returns:
        bytes: Audio data or None if error
    """
    
    # Validate language code
    if language_code not in LANGUAGE_MAP:
        language_code = "en-IN"  # Default to English
    
    url = "https://api.sarvam.ai/text-to-speech"
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Minimal payload with only required fields
    payload = {
        "inputs": [text],
        "target_language_code": language_code,
        "speaker": "anushka",  # Default speaker as per Sarvam docs
        "model": "bulbul:v2"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        # Get audio data (base64 encoded)
        if "audios" in result and len(result["audios"]) > 0:
            audio_base64 = result["audios"][0]
            audio_bytes = base64.b64decode(audio_base64)
            if autoplay:
                _autoplay_audio(audio_bytes)
            return audio_bytes
        else:
            print("No audio data in response")
            return None
            
    except requests.exceptions.HTTPError as e:
        print(f"TTS API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def translate_and_speak(text, target_language="hi-IN", autoplay=True):
    """
    Translate text to target language and convert to speech
    
    Args:
        text: English text to translate and speak
        target_language: Target language code
        autoplay: If True, attempt to play audio automatically
    
    Returns:
        bytes: Audio data or None
    """
    # If already in target language, just convert to speech
    if target_language == "en-IN":
        return text_to_speech(text, target_language, autoplay=autoplay)
    
    # Translate to target language
    try:
        # Use Sarvam AI translation
        translated = translate_from_english(text, target_language)
        if translated:
            return text_to_speech(translated, target_language, autoplay=autoplay)
        else:
            # Fallback: speak in English
            return text_to_speech(text, "en-IN", autoplay=autoplay)
    except:
        # Fallback: speak in English
        return text_to_speech(text, "en-IN", autoplay=autoplay)

def translate_from_english(text, target_language):
    """Translate from English to target language"""
    url = "https://api.sarvam.ai/translate"
    
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": text,
        "source_language_code": "en-IN",
        "target_language_code": target_language,
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1",
        "enable_preprocessing": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("translated_text", text)
    except:
        return text