from flask import Flask, request, jsonify
from hugchat import hugchat
from hugchat.login import Login
import os
import time
import traceback

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
        print(f"Usando email: {EMAIL[:3]}...{EMAIL[-10:] if EMAIL else 'No configurado'}")
        print(f"Password configurado: {'Sí' if PASSWORD else 'No'}")
        print(f"Assistant ID configurado: {'Sí' if ASSISTANT_ID else 'No'}")

        if not all([EMAIL, PASSWORD, ASSISTANT_ID]):
            raise ValueError("Faltan variables de entorno necesarias")

        # Iniciar sesión
        sign = Login(EMAIL, PASSWORD)
        try:
            cookies = sign.login()
            print("Login exitoso")
        except Exception as e:
            print(f"Error en login: {str(e)}")
            print(f"Traceback completo: {traceback.format_exc()}")
            raise

        print("Creando instancia de chatbot...")
        # Crear instancia del chatbot
        chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
        
        print("Creando nueva conversación...")
        # Crear nueva conversación
        chatbot.new_conversation(assistant=ASSISTANT_ID, switch_to=True)
        
        print("Chatbot inicializado correctamente")
        return True
    except Exception as e:
        print(f"Error detallado en la inicialización del chatbot: {str(e)}")
        print(f"Tipo de error: {type(e)}")
        print(f"Traceback completo: {traceback.format_exc()}")
        return False

@app.route('/')
def home():
    return jsonify({"message": "HugChat API está funcionando"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    global chatbot
    try:
        if chatbot is None:
            success = initialize_chatbot()
            if not success:
                return jsonify({
                    "status": "unhealthy",
                    "message": "No se pudo inicializar el chatbot"
                }), 503
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "type": str(type(e))
        }), 500

@app.route('/chat', methods=['POST'])
def chat():
    global chatbot
    try:
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
                return jsonify({"error": "No se pudo inicializar el chatbot"}), 500
        
        print("Enviando solicitud a Hugging Face API...")
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
        print(f"Traceback completo: {traceback.format_exc()}")
        return jsonify({
            "error": str(e),
            "type": str(type(e)),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    # Intentar inicializar el chatbot al inicio
    initialize_chatbot()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)