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

# Cache para el chatbot
@lru_cache(maxsize=1)
def get_chatbot():
    try:
        # Iniciar sesión
        sign = Login(EMAIL, PASSWORD)
        cookies = sign.login()
        
        # Crear instancia del chatbot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
        # Crear nueva conversación
        chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to=True)
        
        return chatbot
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Validar el request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        # Obtener el mensaje
        message = data['message']
        
        # Obtener el chatbot (usando cache)
        chatbot = get_chatbot()
        if not chatbot:
            return jsonify({"error": "Failed to initialize chatbot"}), 500
        
        # Obtener respuesta
        start_time = time.time()
        response = chatbot.chat(message).wait_until_done()
        end_time = time.time()
        
        return jsonify({
            "response": response,
            "processing_time": round(end_time - start_time, 2)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Obtener puerto de Render o usar 5000 como default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)