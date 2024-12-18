from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import os
from typing import List, Dict

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

# La forma correcta de inicializar el cliente
client = InferenceClient(token=os.environ.get("HUGGINGFACE_API_KEY"))

SYSTEM_PROMPT = """Actúa como un consultor experto en la fórmula de Feedback SCI (Situación-Comportamiento-Impacto) de Creative or Creational Leadership. Tu objetivo es ayudarme a dar feedback constructivo y efectivo."""

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.messages
        
        completion = client.text_generation(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            prompt=messages[0]["content"],
            max_new_tokens=500
        )
        
        return {
            "response": completion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API is working!"}