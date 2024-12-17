from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
import os
from functools import lru_cache
import time

app = Flask(__name__)

# Configuración
EMAIL = os.environ.get('HUGGINGFACE_EMAIL')
PASSWORD = os.environ.get('HUGGINGFACE_PASSWORD')
ASSISTANT_ID = os.environ.get('ASSISTANT_ID')

# Variable global para el chatbot
chatbot = None

def initialize_chatbot():
    global chatbot
    try:
        print("Iniciando proceso de login...")
        # Iniciar sesión
        sign = Login(EMAIL, PASSWORD)
        cookies = sign.login()
        
        print("Login exitoso, creando instancia de chatbot...")
        # Crear instancia del chatbot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
        print("Creando nueva conversación...")
        # Crear nueva conversación
        chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to=True)
        
        print("Chatbot inicializado correctamente")
        return True
    except Exception as e:
        print(f"Error en la inicialización del chatbot: {str(e)}")
        return False

@app.before_first_request
def startup():
    initialize_chatbot()

@app.route('/health', methods=['GET'])
def health_check():
    global chatbot
    if chatbot is None:
        return jsonify({"status": "unhealthy", "message": "Chatbot not initialized"}), 503
    return jsonify({"status": "healthy"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    global chatbot
    try:
        # Validar el request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        message = data['message']
        print(f"Mensaje recibido: {message}")
        
        # Verificar si el chatbot está inicializado
        if chatbot is None:
            print("Chatbot no inicializado, intentando inicializar...")
            if not initialize_chatbot():
                return jsonify({"error": "Failed to initialize chatbot"}), 500
        
        print("Enviando solicitud a Hugging Face API...")
        # Obtener respuesta
        start_time = time.time()
        response = chatbot.chat(message)
        result = response.wait_until_done()
        end_time = time.time()
        
        print("Respuesta recibida correctamente")
        return jsonify({
            "response": result,
            "processing_time": round(end_time - start_time, 2)
        }), 200
        
    except Exception as e:
        print(f"Error durante el chat: {str(e)}")
        # Si hay un error de autenticación, intentar reinicializar
        if "Authorization" in str(e):
            print("Error de autenticación detectado, reinicializando chatbot...")
            if initialize_chatbot():
                return jsonify({"error": "Please try again, service reinitialized"}), 503
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)