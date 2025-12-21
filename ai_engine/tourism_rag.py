# tourism_rag.py
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from llm_engine import run_llm
from retriever import retrieve

model = SentenceTransformer("all-MiniLM-L6-v2")
BASE_DIR = os.path.dirname(__file__)

# Load tourism prompt
prompt_path = os.path.join(BASE_DIR, "prompts", "tourism_prompt.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    TOURISM_PROMPT = f.read()

def _search(query, topk=3):
    qv = model.encode([query])[0]
    try:
        return retrieve("tourism_embeds.pt", qv, k=topk)
    except Exception as e:
        print(f"Retrieval error: {e}")
        return []

def answer_tourism_rag(query, lang="en"):
    hits = _search(query, topk=3)
    
    if not hits:
        context = "No specific tourism data found."
    else:
        # hits is a list of (text, score)
        context = "\n\n".join([f"- {h[0]}" for h in hits])
    
    system = TOURISM_PROMPT + f"\n\nSTRICT RULE: Answer ONLY in {lang}. Use separate lines and points.\n\nContext:\n" + context
    return run_llm(system, query)

