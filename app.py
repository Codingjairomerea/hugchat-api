# app.py
from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
import os
import time

app = Flask(__name__)

# Variable global para el chatbot
chatbot = None

def initialize_chatbot():
    global chatbot
    try:
        print("Iniciando proceso de login...")
        # Obtener credenciales de variables de entorno
        email = os.getenv('HUGGINGFACE_EMAIL')
        password = os.getenv('HUGGINGFACE_PASSWORD')
        assistant_id = os.getenv('ASSISTANT_ID')

        if not all([email, password, assistant_id]):
            raise ValueError("Faltan variables de entorno necesarias")

        # Iniciar sesión
        sign = Login(email, password)
        cookies = sign.login()
        
        # Crear instancia del chatbot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
        # Crear nueva conversación
        chatbot.new_conversation(assistant=assistant_id, switch_to=True)
        
        print("Chatbot inicializado correctamente")
        return True
    except Exception as e:
        print(f"Error en la inicialización del chatbot: {str(e)}")
        return False

@app.route('/')
def home():
    return {"status": "API is running"}, 200

@app.route('/chat', methods=['POST'])
def chat():
    global chatbot
    
    try:
        if not request.is_json:
            return {"error": "Request must be JSON"}, 400
        
        data = request.get_json()
        if 'message' not in data:
            return {"error": "Message is required"}, 400
            
        message = data['message']
        
        # Verificar si el chatbot está inicializado
        if chatbot is None:
            if not initialize_chatbot():
                return {"error": "Failed to initialize chatbot"}, 500
        
        # Obtener respuesta
        response = chatbot.chat(message)
        result = response.wait_until_done()
        
        return {"response": result}, 200
        
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    initialize_chatbot()  # Intentar inicializar al arrancar
    app.run(host='0.0.0.0', port=port)