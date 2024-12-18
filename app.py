# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import os
from typing import List, Dict

app = FastAPI()

# Modelo para la request
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

# Inicializar el cliente de Hugging Face
client = InferenceClient(api_key=os.environ.get("HUGGINGFACE_API_KEY"))

# Instrucción del sistema para el feedback SCI
SYSTEM_PROMPT = """Actúa como un consultor experto en la fórmula de Feedback SCI (Situación-Comportamiento-Impacto) de Creative or Creational Leadership. Tu objetivo es ayudarme a dar feedback constructivo y efectivo. Cuando te presente una situación donde necesito dar feedback, necesito que me guíes para estructurarlo con la fórmula SCI. Tus respuestas deben ser resumidas pudiendo llegar como máximo a 500 caracteres."""

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Agregar el system prompt al inicio de los mensajes
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + request.messages
        
        completion = client.chat.completions.create(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            messages=messages,
            max_tokens=500
        )
        
        return {
            "response": completion.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))