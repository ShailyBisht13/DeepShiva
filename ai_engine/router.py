# =========================================================
# router.py — UPDATED FOR INTERACTIVE MEDITATION
# =========================================================
import requests
import re
import os
import threading
from typing import Optional

from intent_classifier import classify_intent
from llm_engine import run_llm
from tourism_rag import answer_tourism_rag
from spiritual_rag import answer_spiritual_rag
from monuments_ai import recognize_monument
from yoga_client import detect_yoga

# Optional modules
try:
    from voice_output import generate_tts_audio
except Exception:
    generate_tts_audio = None

try:
    from meditation_engine import generate_meditation_audio
except Exception:
    generate_meditation_audio = None


# =========================================================
# 🔑 API KEYS & CONFIG
# =========================================================
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")

LANG_MAP = {
    "en": {"name": "English", "tts": "en"},
    "hi": {"name": "Hindi", "tts": "hi"},
    "sa": {"name": "Sanskrit", "tts": None},
    "mr": {"name": "Marathi", "tts": "mr"},
    "bn": {"name": "Bengali", "tts": "bn"},
}

def shiva_intro(lang="en"):
    return {
        "hi": "मैं SHIVA BOT हूँ — आपका पर्यटन एवं आध्यात्मिक सहायक।\n\n",
        "sa": "अहं SHIVA BOT अस्मि — तव पर्यटन–आध्यात्मिक सहायकः।\n\n",
        "mr": "मी SHIVA BOT आहे — तुमचा पर्यटन व आध्यात्मिक सहायय्यक.\n\n",
        "bn": "আমি SHIVA BOT — আপনার পর্যটন ও আধ্যাত্মিক সহকারী।\n\n",
    }.get(lang, "I am SHIVA BOT — your Tourism & Spiritual assistant.\n\n")

# =========================================================
# 🧘 MEDITATION LOGIC (INTERACTIVE)
# =========================================================
def handle_meditation(lang, query):
    q = query.lower()
    
    # 1. Detect selection keywords
    choice = None
    if "forest" in q or "जंगल" in q: choice = "forest"
    elif "river" in q or "नदी" in q: choice = "river"
    elif "wind" in q or "हवा" in q: choice = "wind"
    elif "rain" in q or "बारिश" in q: choice = "rain"

    # 2. If a choice is detected, start it
    if choice:
        if generate_meditation_audio:
            # We now run this synchronously so we can return the audio_url
            med_result = generate_meditation_audio(language=lang, ambience=choice, duration_sec=60)
            
            if med_result.get("status") == "ok":
                msgs = {
                    "en": f"Starting 1-minute meditation with {choice} sounds. Relax...",
                    "hi": f"{choice} की आवाज़ के साथ 1 मिनट का ध्यान शुरू हो रहा है। शांत रहें..."
                }
                reply = msgs.get(lang, msgs["en"])
                return {"answer": reply, "audio_url": med_result.get("audio_url")}
            else:
                return f"Meditation error: {med_result.get('message')}"
        else:
            return "Meditation service currently unavailable."

    # 3. If no choice detected, Ask the user
    questions = {
        "en": "Which sound would you like for your meditation? (Forest, River, Wind, or Rain?)",
        "hi": "आप ध्यान के लिए कौन सी आवाज़ पसंद करेंगे? (जंगल, नदी, हवा, या बारिश?)"
    }
    return questions.get(lang, questions["en"])

# =========================================================
# 🚦 MAIN ROUTER
# =========================================================
def ai_router(
    user_input: str,
    lang: str = "en",
    persona: str = "guide",
    image_path: Optional[str] = None
):
    lang = lang if lang in LANG_MAP else "en"
    intent = classify_intent(user_input)
    q = user_input.lower()

    # ---------- WEATHER ----------
    if "weather" in q:
        # Internal helper (No external router_utils import needed)
        try:
            def _get_weather_local(query):
                place = re.sub(r"(weather|in|of|tell me)", "", query.lower()).strip()
                if not place: return {"status": "error", "message": "Place?"}
                r = requests.get("https://api.openweathermap.org/data/2.5/weather", params={"q": place, "appid": OPENWEATHER_API_KEY, "units": "metric"}, timeout=4)
                if r.status_code == 200:
                    d = r.json()
                    return {"status": "ok", "location": place.title(), "temperature": f"{d['main']['temp']}°C", "condition": d["weather"][0]["description"]}
                return {"status": "error", "message": "Not found"}

            result = {"status": "ok", "intent": "weather", "answer": _get_weather_local(user_input), "lang": lang}
        except Exception as e:
            result = {"status": "ok", "intent": "weather", "answer": f"Weather error: {e}", "lang": lang}

    # ---------- MEDITATION (NEW INTERACTIVE) ----------
    elif intent == "meditation" or any(x in q for x in ["forest", "river", "wind", "rain"]):
        med_res = handle_meditation(lang, user_input)
        
        if isinstance(med_res, dict):
            answer = shiva_intro(lang) + med_res.get("answer", "")
            audio_url = med_res.get("audio_url")
        else:
            answer = shiva_intro(lang) + med_res
            audio_url = None

        result = {
            "status": "ok",
            "intent": "meditation",
            "answer": answer,
            "audio_url": audio_url,
            "lang": lang
        }

    # ---------- YOGA ----------
    elif intent == "yoga":
        if not image_path or not os.path.isfile(image_path):
            result = {"status": "need_image", "intent": "yoga", "answer": "Upload yoga pose image.", "lang": lang}
        else:
            yoga_response = detect_yoga(image_path)
            result = {"status": "ok", "intent": "yoga", "answer": yoga_response, "lang": lang}

    # ---------- MONUMENT ----------
    elif intent == "monument":
        if not image_path or not os.path.isfile(image_path):
            result = {"status": "need_image", "message": "Upload monument image.", "lang": lang}
        else:
            result = {"status": "ok", "intent": "monument", "answer": recognize_monument(image_path), "lang": lang}

    # ---------- SPIRITUAL / TOURISM ----------
    elif intent == "spiritual":
        result = {"status": "ok", "intent": "spiritual", "answer": shiva_intro(lang) + answer_spiritual_rag(user_input, lang=lang), "lang": lang}
    elif intent == "tourism":
        result = {"status": "ok", "intent": "tourism", "answer": shiva_intro(lang) + answer_tourism_rag(user_input, lang=lang), "lang": lang}

    # ---------- GENERAL ----------
    else:
        prompt = f"You are SHIVA BOT. Answer ONLY in {LANG_MAP[lang]['name']}. Use separate lines and point-wise structure to make your response easy to read."
        final = shiva_intro(lang) + run_llm(prompt, user_input)
        result = {"status": "ok", "intent": "general", "answer": final, "lang": lang}

    # ---------- SERVER-SIDE TTS (NEW) ----------
    # We generate the audio file so the frontend can play it via URL.
    if generate_tts_audio and isinstance(result.get("answer"), str):
        # Meditation already has its own audio_url (ambient sounds)
        if result.get("intent") != "meditation":
            tts_lang = LANG_MAP[lang]["tts"] or "en"
            audio_url = generate_tts_audio(result["answer"], lang=tts_lang)
            if audio_url:
                result["audio_url"] = audio_url

    return result
