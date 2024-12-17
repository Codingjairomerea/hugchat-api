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
        print("=== Diagnóstico de Variables de Entorno ===")
        # Obtener y verificar cada variable
        email = os.getenv('HUGGINGFACE_EMAIL')
        password = os.getenv('HUGGINGFACE_PASSWORD')
        assistant_id = os.getenv('ASSISTANT_ID')
        
        # Imprimir estado de cada variable (de forma segura)
        print(f"HUGGINGFACE_EMAIL: {'Configurado' if email else 'No configurado'}")
        print(f"HUGGINGFACE_PASSWORD: {'Configurado' if password else 'No configurado'}")
        print(f"ASSISTANT_ID: {'Configurado' if assistant_id else 'No configurado'}")
        
        if not all([email, password, assistant_id]):
            missing_vars = []
            if not email: missing_vars.append("HUGGINGFACE_EMAIL")
            if not password: missing_vars.append("HUGGINGFACE_PASSWORD")
            if not assistant_id: missing_vars.append("ASSISTANT_ID")
            print(f"Variables faltantes: {', '.join(missing_vars)}")
            raise ValueError(f"Faltan las siguientes variables: {', '.join(missing_vars)}")

        print("Iniciando login con Hugging Face...")
        sign = Login(email, password)
        cookies = sign.login()
        
        print("Login exitoso, creando instancia de chatbot...")
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
        print("Configurando nueva conversación...")
        chatbot.new_conversation(assistant=assistant_id, switch_to=True)
        
        print("Chatbot inicializado correctamente")
        return True
    except Exception as e:
        print(f"Error detallado: {str(e)}")
        return False

@app.route('/')
def home():
    return jsonify({
        "status": "API is running",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }), 200

@app.route('/check-env', methods=['GET'])
def check_env():
    # Endpoint seguro para verificar variables
    return jsonify({
        "variables_configured": {
            "HUGGINGFACE_EMAIL": bool(os.getenv('HUGGINGFACE_EMAIL')),
            "HUGGINGFACE_PASSWORD": bool(os.getenv('HUGGINGFACE_PASSWORD')),
            "ASSISTANT_ID": bool(os.getenv('ASSISTANT_ID'))
        }
    })

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
                return jsonify({"error": "Failed to initialize chatbot"}), 500
        
        print("Procesando mensaje...")
        response = chatbot.chat(message)
        result = response.wait_until_done()
        
        print("Respuesta generada exitosamente")
        return jsonify({"response": result}), 200
        
    except Exception as e:
        print(f"Error en el chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Iniciando aplicación...")
    initialize_chatbot()
    app.run(host='0.0.0.0', port=port)