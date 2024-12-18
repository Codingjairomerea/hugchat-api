from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import os
from typing import List, Dict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

client = InferenceClient(token=os.environ.get("HUGGINGFACE_API_KEY"))

SYSTEM_PROMPT = """Actúa como un consultor experto en la fórmula de Feedback SCI (Situación-Comportamiento-Impacto) de Creative or Creational Leadership. Tu objetivo es ayudarme a dar feedback constructivo y efectivo."""

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Recibida solicitud con mensajes: {request.messages}")
        
        # Construir el prompt completo
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {request.messages[0]['content']}"
        logger.info(f"Prompt completo: {full_prompt}")
        
        # Llamar a la API
        logger.info("Llamando a Hugging Face API...")
        completion = client.text_generation(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            prompt=full_prompt,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True
        )
        
        logger.info(f"Respuesta recibida: {completion}")
        
        if not completion:
            raise HTTPException(status_code=500, detail="No se recibió respuesta del modelo")
        
        return {
            "response": completion,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error en el procesamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API is working!"}