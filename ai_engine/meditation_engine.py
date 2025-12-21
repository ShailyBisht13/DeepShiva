# meditation_engine.py — UPDATED TO RETURN FILE PATH
import os
import time
import uuid
from gtts import gTTS
from pydub import AudioSegment

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Target directory for frontend access - backend/uploads/meditation
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "backend", "uploads", "meditation")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_meditation_audio(
        language="en",
        ambience="forest",
        duration_sec=60,
        script_text=None
):
    temp_voice = os.path.join(BASE_DIR, f"voice_{uuid.uuid4()}.mp3")
    final_filename = f"meditation_{uuid.uuid4()}.mp3"
    final_path = os.path.join(UPLOAD_DIR, final_filename)
    
    try:
        # 1. Text (Log it but don't generate voice)
        safe_text = str(script_text or "No script")
        print(f"[DEBUG] Meditation text (Skipped for audio): {safe_text[:30]}...")

        # 2. Skip TTS - Creating a silent base instead
        target_ms = duration_sec * 1000
        # voice = AudioSegment.silent(duration=target_ms) # We'll just use the ambient directly
        
        # 3. Ambient
        ambient = None
        sounds_dir = os.path.join(BASE_DIR, "sounds")
        ambience_file = os.path.join(sounds_dir, f"{ambience}.mp3")
        
        if os.path.exists(ambience_file):
            try:
                print(f"[DEBUG] Loading ambient sound: {ambience_file}")
                ambient = AudioSegment.from_mp3(ambience_file)
            except Exception as e:
                print(f"[WARNING] Could not load ambient sound {ambience_file}: {e}")
        
        if ambient:
            # Repeat ambient to match duration
            ambient = ambient * ((target_ms // len(ambient)) + 1)
            final_audio = ambient[:target_ms]
        else:
            # Fallback to silence if ambient missing
            print("[WARNING] No ambient sound found, generating silence.")
            final_audio = AudioSegment.silent(duration=target_ms)

        # 4. Save
        print(f"[DEBUG] Saving final ambient audio to: {final_path}")
        final_audio.export(final_path, format="mp3")
        
        # Return relative URL for frontend
        return {"status": "ok", "audio_url": f"/uploads/meditation/{final_filename}", "message": "Meditation ready."}

    except Exception as e:
        print(f"Meditation Engine Error: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        # 5. Cleanup
        if os.path.exists(temp_voice):
            for i in range(5):
                try:
                    os.remove(temp_voice)
                    break
                except Exception:
                    time.sleep(0.5)
