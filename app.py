# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import json

# Cargar variables de entorno
load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    try:
        # Verificar token
        api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        return jsonify({
            'status': 'API is running',
            'token_configured': bool(api_token)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        print("Recibida petición POST a /chat")
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        print("Mensaje recibido:", data['message'])

        # Obtener token
        api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        if not api_token:
            return jsonify({'error': 'API token not configured'}), 500

        # URL del modelo
        API_URL = f"https://api-inference.huggingface.co/models/chat/assistant/67462b5e2eb7c0162d496b12"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        # Preparar payload
        payload = {
            "inputs": data['message'],
            "parameters": {
                "max_length": 500,
                "temperature": 0.7,
                "top_p": 0.95
            }
        }

        print("Enviando solicitud a Hugging Face API...")
        
        # Hacer la solicitud al API
        response = requests.post(API_URL, headers=headers, json=payload)
        
        print("Respuesta recibida del API:", response.status_code)
        print("Contenido de la respuesta:", response.text)

        if response.status_code == 200:
            response_data = response.json()
            return jsonify({'response': response_data[0]['generated_text']})
        else:
            return jsonify({
                'error': 'Error from Hugging Face API',
                'details': response.text
            }), response.status_code

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

# Esta línea es importante para Gunicorn
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)