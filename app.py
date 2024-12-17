from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
import os
import time
import json
import requests

app = Flask(__name__)

# Variable global para el chatbot
chatbot = None

def initialize_chatbot():
    global chatbot
    try:
        print("=== Diagnóstico de Variables de Entorno ===")
        email = os.getenv('HUGGINGFACE_EMAIL')
        password = os.getenv('HUGGINGFACE_PASSWORD')
        assistant_id = os.getenv('ASSISTANT_ID')
        
        print(f"HUGGINGFACE_EMAIL: {'Configurado' if email else 'No configurado'}")
        print(f"HUGGINGFACE_PASSWORD: {'Configurado' if password else 'No configurado'}")
        print(f"ASSISTANT_ID: {'Configurado' if assistant_id else 'No configurado'}")

        if not all([email, password, assistant_id]):
            missing_vars = []
            if not email: missing_vars.append("HUGGINGFACE_EMAIL")
            if not password: missing_vars.append("HUGGINGFACE_PASSWORD")
            if not assistant_id: missing_vars.append("ASSISTANT_ID")
            raise ValueError(f"Faltan las siguientes variables: {', '.join(missing_vars)}")

        print("Iniciando login con Hugging Face...")
        
        # Nuevo método de login
        sign = Login(email, password)
        try:
            # Intentar el login con manejo de errores específico
            cookies = sign.login()
            if not cookies:
                raise Exception("No se obtuvieron cookies en el login")
            
            print("Login exitoso, verificando cookies...")
            cookie_dict = cookies.get_dict()
            if not cookie_dict:
                raise Exception("Diccionario de cookies vacío")
                
            print("Cookies obtenidas correctamente")
            
        except Exception as e:
            print(f"Error en el proceso de login: {str(e)}")
            # Intentar método alternativo de login
            try:
                print("Intentando método alternativo de login...")
                session = requests.Session()
                sign.login(session=session)  # Usar sesión explícita
                cookies = session.cookies
                print("Login alternativo exitoso")
            except Exception as e2:
                print(f"Error en método alternativo: {str(e2)}")
                raise Exception(f"Falló login principal ({str(e)}) y alternativo ({str(e2)})")

        print("Creando instancia de chatbot...")
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
        print("Configurando nueva conversación...")
        chatbot.new_conversation(assistant=assistant_id, switch_to=True)
        
        print("Chatbot inicializado correctamente")
        return True
        
    except Exception as e:
        print(f"Error detallado en initialize_chatbot: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        return False

@app.route('/')
def home():
    return jsonify({
        "status": "API is running",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@app.route('/chat', methods=['POST'])
def chat():
    global chatbot
    try:
        print("=== Nueva solicitud de chat ===")
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
            
        message = data['message']
        print(f"Mensaje recibido: {message}")
        
        if chatbot is None:
            print("Chatbot no inicializado, intentando inicializar...")
            if not initialize_chatbot():
                return jsonify({"error": "No se pudo inicializar el chatbot. Verifica las credenciales."}), 500
        
        print("Procesando mensaje...")
        try:
            response = chatbot.chat(message)
            result = response.wait_until_done()
            print("Respuesta generada exitosamente")
            return jsonify({"response": result}), 200
        except Exception as chat_error:
            print(f"Error en el chat, reinicializando chatbot...")
            chatbot = None
            if not initialize_chatbot():
                raise Exception("No se pudo reinicializar el chatbot")
            response = chatbot.chat(message)
            result = response.wait_until_done()
            return jsonify({"response": result}), 200
            
    except Exception as e:
        print(f"Error en el chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Iniciando aplicación...")
    initialize_chatbot()
    app.run(host='0.0.0.0', port=port)