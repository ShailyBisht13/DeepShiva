# voice_output.py — UPDATED FOR SERVER-SIDE TTS GENERATION
import os
import uuid
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Save to backend/uploads/tts
TTS_DIR = os.path.join(os.path.dirname(BASE_DIR), "backend", "uploads", "tts")

if not os.path.exists(TTS_DIR):
    os.makedirs(TTS_DIR, exist_ok=True)

def generate_tts_audio(text, lang="en"):
    """
    Generates a TTS file and returns the relative URL.
    Does NOT play audio on the server.
    """
    filename = f"tts_{uuid.uuid4()}.mp3"
    filepath = os.path.join(TTS_DIR, filename)
    
    try:
        if isinstance(text, (dict, list)):
            text = str(text)
        text = (text or "").strip()
        if not text:
            return None

        # Generate gTTS
        tts = gTTS(text=text, lang=lang)
        tts.save(filepath)
        
        # Return relative path for frontend
        return f"/uploads/tts/{filename}"

    except Exception as e:
        print(f"TTS Generation Error: {e}")
        return None

# Keep a mock speak for backward compatibility but disable it
def speak(text, lang="en"):
    pass
