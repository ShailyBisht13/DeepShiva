# ai_engine/spiritual_rag.py
import os
import torch
from llm_engine import run_llm
from retriever import retrieve
from sentence_transformers import SentenceTransformer
from dataset_loader import load_temples, load_shlokas, load_spiritual_data

BASE_DIR = os.path.dirname(__file__)
SPIRITUAL_PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "spiritual_prompt.txt")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------
# Load system prompt
# -------------------------
def _load_prompt():
    if not os.path.exists(SPIRITUAL_PROMPT_PATH):
        print(f"Warning: Spiritual prompt missing at {SPIRITUAL_PROMPT_PATH}")
        return "You are a spiritual assistant."
    with open(SPIRITUAL_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = _load_prompt()


# -------------------------
# Format temples (supports list OR dict)
# -------------------------
def format_temples(temple_data):
    if not temple_data:
        return ""

    formatted = []

    # Case 1: temple_data is dict
    if isinstance(temple_data, dict):
        for name, info in temple_data.items():
            significance = info.get("significance", "")
            formatted.append(f"{name}: {significance}")

    # Case 2: temple_data is list
    elif isinstance(temple_data, list):
        for entry in temple_data:
            name = entry.get("temple") or entry.get("name") or "Unknown Temple"
            significance = entry.get("significance", "")
            formatted.append(f"{name}: {significance}")

    return "\n".join(formatted)


# ---------------------------------------------------------
# Main Spiritual RAG Answering Function
# ---------------------------------------------------------
def answer_spiritual_rag(query, lang="en", top_k=3):
    q_emb = embed_model.encode(query, convert_to_tensor=True)

    # RAG — Shlokas
    try:
        shl_results = retrieve("shlokas_embeds.pt", q_emb, k=top_k)
        shl_text = "\n".join([f"- {t[:400]} (score={s:.3f})" for t, s in shl_results])
    except:
        shl_text = "No shloka embeddings found."

    # Load temples safely
    temple_data = load_temples()
    temple_text = format_temples(temple_data)

    # Combine context
    context = f"""
Shlokas:
{shl_text}

Temples:
{temple_text}
"""

    final_input = f"{context}\n\nUser Question: {query}"

    prompt = SYSTEM_PROMPT + f"\n\nSTRICT RULE: Answer ONLY in {lang}. Use separate lines and points.\n"
    # Send to LLM
    return run_llm(prompt, final_input)
