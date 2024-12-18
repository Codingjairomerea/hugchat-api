from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import os
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

class ChatResponse(BaseModel):
    response: str
    status: str

client = InferenceClient(token=os.environ.get("HUGGINGFACE_API_KEY"))

SYSTEM_PROMPT = """Eres un consultor experto en feedback constructivo. Tu tarea es ayudar a los usuarios a aplicar la fórmula SCI: Situación (dónde y cuando ocurrió extactamente), Comportamiento (qué se hizo o no se hizo) e Impacto (cómo impacto en ti emocionalmente esa actitud). Al recibir una descripción, guía al usuario a identificar cada elemento y a construir un feedback claro y enfocado en el desarrollo. Tus respuestas deben ser concisas y útiles"""

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Recibida solicitud con mensajes: {request.messages}")
        
        # Construir el prompt completo
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {request.messages[0]['content']}\nAssistant:"
        logger.info(f"Prompt completo: {full_prompt}")
        
        # Llamar a la API
        logger.info("Llamando a Hugging Face API...")
        completion = client.text_generation(
            model="mistralai/Mistral-Nemo-Instruct-2407",
            prompt=full_prompt,
            max_new_tokens=500,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            top_k=50
        )
        
        logger.info(f"Respuesta recibida: {completion}")
        
        return ChatResponse(
            response=str(completion).strip(),
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error en el procesamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))