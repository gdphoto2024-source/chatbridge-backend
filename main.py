from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# =========================
# CONFIG
# =========================
# Ollama di default ascolta qui (locale)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b-instruct")

# (opzionale) LibreTranslate self-host / pubblico
# Esempio pubblico: https://libretranslate.com (può avere limiti)
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "")

# =========================
# ROUTE TEST
# =========================
@app.get("/")
def root():
    return {"status": "ok", "service": "chatbridge-backend", "mode": "ollama"}

# =========================
# MODELLI INPUT
# =========================
class AIRequest(BaseModel):
    prompt: str
    context: str

class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"
    target: str = "en"

# =========================
# HELPERS
# =========================
def ollama_chat(system: str, user: str) -> str:
    """
    Chiama Ollama /api/chat (non streaming) e ritorna solo il testo.
    Docs: POST /api/chat :contentReference[oaicite:3]{index=3}
    """
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()
    return (data.get("message") or {}).get("content", "").strip()

def libretranslate(text: str, source: str, target: str) -> str:
    """
    Chiama LibreTranslate POST /translate :contentReference[oaicite:4]{index=4}
    """
    if not LIBRETRANSLATE_URL:
        raise RuntimeError("LIBRETRANSLATE_URL non configurata")
    payload = {"q": text, "source": source, "target": target, "format": "text"}
    r = requests.post(f"{LIBRETRANSLATE_URL}/translate", data=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    # libretranslate ritorna tipicamente {"translatedText":"..."}
    return (data.get("translatedText") or "").strip()

# =========================
# ENDPOINT AI (Chat/Riscrivi/Comandi)
# =========================
@app.post("/ai")
def ai_endpoint(data: AIRequest):
    """
    Usa Ollama per:
    - rispondere tipo ChatGPT
    - riscrivere
    - qualsiasi comando (prompt)
    """
    try:
        system = "Sei un assistente utile. Rispondi in modo chiaro e conciso."
        user = f"ISTRUZIONE:\n{data.prompt}\n\nTESTO/CONTESTO:\n{data.context}"
        text = ollama_chat(system=system, user=user)
        return {"text": text}
    except Exception as e:
        return {"text": f"Errore AI (Ollama): {e}"}

# =========================
# ENDPOINT TRADUZIONE (opzionale)
# =========================
@app.post("/translate")
def translate_endpoint(data: TranslateRequest):
    """
    Traduzione gratis usando LibreTranslate (se configurato).
    """
    try:
        translated = libretranslate(text=data.text, source=data.source, target=data.target)
        return {"text": translated}
    except Exception as e:
        return {"text": f"Errore traduzione: {e}"}
