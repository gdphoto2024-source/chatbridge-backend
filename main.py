from fastapi import FastAPI
from pydantic import BaseModel
import os
import requests

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class AIRequest(BaseModel):
    prompt: str
    context: str

@app.post("/ai")
def ai_endpoint(data: AIRequest):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{data.prompt}\n\nText:\n{data.context}"}
            ]
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )

        result = response.json()
        text = result["choices"][0]["message"]["content"]

        return {"text": text}

    except Exception as e:
        return {"text": f"Errore: {str(e)}"}