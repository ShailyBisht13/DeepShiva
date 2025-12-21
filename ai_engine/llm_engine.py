import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config/keys.env")

api_key = os.getenv("GROQ_API_KEY")
if api_key is None:
    raise ValueError("GROQ_API_KEY is missing. Please set it in config/keys.env")

client = Groq(api_key=api_key)

def run_llm(system_prompt, user_text):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content  # ✅ FIXED
