from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# Prende la chiave OpenAI dalle variabili ambiente di Render
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# =============================
# ROUTE TEST (controllo server)
# =============================
@app.get("/")
def root():
    return {"status": "ok", "service": "chatbridge-backend"}


# =============================
# MODELLO RICHIESTA
# =============================
class AIRequest(BaseModel):
    prompt: str
    context: str


# =============================
# ENDPOINT AI
# =============================
@app.post("/ai")
def ai_endpoint(data: AIRequest):
    try:
        if not OPENAI_API_KEY:
            return {"text": "Errore: OPENAI_API_KEY non configurata"}

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",  # modello economico e veloce
            "messages": [
                {"role": "system", "content": "Sei un assistente utile."},
                {
                    "role": "user",
                    "content": f"{data.prompt}\n\nTesto:\n{data.context}"
                }
            ]
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()

        if "choices" not in result:
            return {"text": f"Errore API: {result}"}

        text = result["choices"][0]["message"]["content"]

        return {"text": text}

    except Exception as e:
        return {"text": f"Errore interno: {str(e)}"}
