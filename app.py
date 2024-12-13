# app.py
from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'API is running'})

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        # Obtener credenciales
        email = os.getenv('HUGGINGFACE_EMAIL')
        password = os.getenv('HUGGINGFACE_PASSWORD')
        
        # Login
        sign = Login(email, password)
        cookies = sign.login()
        
        # Crear chatbot
        chatbot = hugchat.ChatBot(cookies=cookies)
        
        # Cambiar al asistente específico
        assistant_id = '67462b5e2eb7c0162d496b12'
        chatbot.switch_assistant(assistant_id)
        
        # Obtener respuesta
        response = chatbot.chat(data['message'])
        
        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Esta línea es importante para Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)