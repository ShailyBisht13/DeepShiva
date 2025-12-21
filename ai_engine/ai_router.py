from language_engine import detect_language
from intent_classifier import classify_intent
from persona_manager import get_persona
from llm_engine import run_llm

from tourism_rag import answer_tourism_rag
from spiritual_rag import answer_spiritual_rag
from monuments_ai import recognize_monument
from yoga_client import detect_yoga
from realtime_services import get_live_weather, get_live_crowd
from crowd_prediction import predict_crowd

try:
    from voice_output import speak
except Exception:
    speak = None




LANG_MAP = {
    "en": {"name": "English", "tts": "en"},
    "hi": {"name": "Hindi", "tts": "hi"},
    "mr": {"name": "Marathi", "tts": "mr"},
    "bn": {"name": "Bengali", "tts": "bn"},
    "sa": {"name": "Sanskrit", "tts": None}
}


def ai_router(user_input, image_path=None, persona_name="travel_guide"):
    # -----------------------------
    # 1. Language & Intent
    # -----------------------------
    lang = detect_language(user_input)
    lang = lang if lang in LANG_MAP else "en"

    intent = classify_intent(user_input)
    persona_prompt = get_persona(persona_name)

    q = user_input.lower()

    # -----------------------------
    # 🚻 TOILET (ABSOLUTE OVERRIDE)
    # -----------------------------
    if any(x in q for x in [
        "toilet", "washroom", "bathroom",
        "शौचालय", "स्वच्छतागृह",
        "টয়লেট", "শৌচালয়"
    ]):
        reply = {
            "en": "🚻 Public toilets are available near the main market and GMVN guest house.",
            "hi": "🚻 सार्वजनिक शौचालय मुख्य बाजार और GMVN विश्रामगृह के पास उपलब्ध हैं।",
            "mr": "🚻 मुख्य बाजार व GMVN विश्रामगृहाजवळ सार्वजनिक शौचालये उपलब्ध आहेत.",
            "bn": "🚻 প্রধান বাজার ও GMVN অতিথিশালার কাছে পাবলিক টয়লেট রয়েছে।"
        }.get(lang)

        if speak and LANG_MAP[lang]["tts"]:
            speak(reply, lang=LANG_MAP[lang]["tts"])

        return {"intent": "toilet", "lang": lang, "answer": reply}

    # -----------------------------
    # 🌦 WEATHER
    # -----------------------------
    if "weather" in q or "मौसम" in q or "हवामान" in q or "আবহাওয়া" in q:
        reply = get_live_weather(user_input)
        return {"intent": "weather", "lang": lang, "answer": reply}

    # -----------------------------
    # 🧘 YOGA (HARD-SANITIZED — FIXED)
    # -----------------------------
    if intent == "yoga":
        if not image_path:
            return {
                "status": "ok",
                "intent": "yoga",
                "lang": lang,
                "answer": "Please upload a yoga pose image."
            }

        raw = detect_yoga(image_path)

        # 🔥 ABSOLUTE SANITIZATION
        if isinstance(raw, dict):
            if raw.get("pose", "").strip() == "Pose detected successfully!":
                raw = {
                    "pose": "Pose detected",
                    "feedback": [
                        "✔ Yoga posture detected",
                        "✔ Detailed posture feedback unavailable (legacy response blocked)"
                    ]
                }
        else:
            raw = {
                "pose": "Yoga analysis failed",
                "feedback": ["Invalid yoga response format"]
            }

        return {
            "status": "ok",
            "intent": "yoga",
            "lang": lang,
            "answer": raw
        }

    # -----------------------------
    # 🏛 MONUMENT
    # -----------------------------
    if intent == "monument":
        if not image_path:
            return {"intent": "monument", "lang": lang, "answer": "Upload monument image."}
        return {"intent": "monument", "lang": lang, "answer": recognize_monument(image_path)}

    # -----------------------------
    # 🔱 SPIRITUAL
    # -----------------------------
    if intent == "spiritual":
        ans = answer_spiritual_rag(user_input)
        if not ans:
            ans = {
                "mr": "आध्यात्मिक माहिती सध्या उपलब्ध नाही.",
                "bn": "আধ্যাত্মিক তথ্য বর্তমানে উপলব্ধ নয়।",
                "en": "Spiritual information temporarily unavailable."
            }.get(lang)
        return {"intent": "spiritual", "lang": lang, "answer": ans}

    # -----------------------------
    # 🌍 TOURISM
    # -----------------------------
    if intent == "tourism":
        ans = answer_tourism_rag(user_input)
        if not ans:
            ans = "Tourism data temporarily unavailable."
        return {"intent": "tourism", "lang": lang, "answer": ans}

    # -----------------------------
    # 🤖 LLM FALLBACK
    # -----------------------------
    prompt = (
        f"{persona_prompt}\n\n"
        f"STRICT RULE:\n"
        f"- Reply ONLY in {LANG_MAP[lang]['name']}\n"
        f"- Do NOT mix languages\n"
    )

    final = run_llm(prompt, user_input)

    if speak and LANG_MAP[lang]["tts"]:
        speak(final, lang=LANG_MAP[lang]["tts"])

    return {"intent": "general", "lang": lang, "answer": final}
