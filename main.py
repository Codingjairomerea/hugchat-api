from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import os
from typing import List, Dict
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

client = InferenceClient(token=os.environ.get("HUGGINGFACE_API_KEY"))

SYSTEM_PROMPT = """Eres un consultor experto en feedback constructivo. Tu tarea es ayudar a los usuarios a aplicar la fórmula SCI: Situación (dónde y cuando ocurrió extactamente), Comportamiento (qué se hizo o no se hizo) e Impacto (cómo impactó en el que brinda el feedback emocionalmente esa actitud, solo como le impactó emocionalmente al que brinda el feedback). Al recibir una descripción, guía al usuario a identificar cada elemento y a construir un feedback claro y enfocado en el desarrollo. Tus respuestas deben ser concisas y útiles"""

# Ruta raíz
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Mistral. Usa /chat para interactuar con el modelo."}

# Ruta de healthcheck
@app.get("/health")
async def health_check():
    return {"status": "OK"}

# Ruta principal del chat
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Recibida solicitud con mensajes: {request.messages}")
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {request.messages[0]['content']}\nAssistant:"
        logger.info(f"Prompt completo: {full_prompt}")
        
        logger.info("Llamando a Hugging Face API...")
        completion = client.text_generation(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            prompt=full_prompt,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True
        )
        
        logger.info(f"Respuesta recibida: {completion}")
        
        response_data = {
            "response": str(completion).strip(),
            "status": "success"
        }
        
        return Response(
            content=json.dumps(response_data),
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error en el procesamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))