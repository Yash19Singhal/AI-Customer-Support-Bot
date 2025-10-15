
import os
import openai

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

def llm_fallback(user_query, context="", max_tokens=150):
    if not OPENAI_KEY:
        return None
    openai.api_key = OPENAI_KEY
    prompt = f"Context:\n{context}\n\nUser: {user_query}\nAssistant (concise answer):"
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini", 
            messages=[{"role":"system","content":"You are a helpful customer support assistant."},
                      {"role":"user","content":prompt}],
            max_tokens=max_tokens,
            temperature=0.2
        )
        return resp['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("LLM fallback failed:", e)
        return None
