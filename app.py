# app.py
from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
from flask_cors import CORS
import os
from dotenv import load_dotenv
import traceback

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    try:
        # Verificar variables de entorno
        email = os.getenv('HUGGINGFACE_EMAIL')
        password = os.getenv('HUGGINGFACE_PASSWORD')
        
        env_status = {
            'status': 'API is running',
            'email_configured': bool(email),
            'password_configured': bool(password)
        }
        return jsonify(env_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Log de la petición recibida
        print("Recibida petición POST a /chat")
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        print("Mensaje recibido:", data['message'])

        # Obtener y verificar credenciales
        email = os.getenv('HUGGINGFACE_EMAIL')
        password = os.getenv('HUGGINGFACE_PASSWORD')
        
        if not email or not password:
            return jsonify({'error': 'Credentials not configured'}), 500
            
        print("Iniciando login en HuggingFace...")
        
        # Login
        sign = Login(email, password)
        cookies = sign.login()
        
        print("Login exitoso, creando chatbot...")
        
        # Crear chatbot
        chatbot = hugchat.ChatBot(cookies=cookies)
        
        print("Cambiando al asistente específico...")
        
        # Cambiar al asistente específico
        assistant_id = '67462b5e2eb7c0162d496b12'
        chatbot.switch_assistant(assistant_id)
        
        print("Enviando mensaje al chatbot...")
        
        # Obtener respuesta
        response = chatbot.chat(data['message'])
        
        print("Respuesta recibida:", response)
        
        return jsonify({'response': response})

    except Exception as e:
        error_traceback = traceback.format_exc()
        print("Error completo:", error_traceback)
        return jsonify({
            'error': str(e),
            'traceback': error_traceback
        }), 500

# Esta línea es importante para Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)