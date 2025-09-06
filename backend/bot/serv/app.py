from flask import Flask, request, jsonify
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from flask_cors import CORS
from dotenv import load_dotenv
from services.app_service import CHATBOT
import os 
import base64

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {  
            "origins": "*",  
            "methods": [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "OPTIONS",
            ],  
            "allow_headers": "*",  
            "expose_headers": "*", 
            "supports_credentials": True,
            "max_age": 86400,
        }},
)

load_dotenv()

bot_service = CHATBOT()

@app.route('/start-chat', methods=['POST'])
def start_chat():
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        response = bot_service.start_chat(user_id)
        
        return jsonify(response)
    
    except Exception as e:
        print(f"Error starting chat: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
@app.route('/message', methods=['POST'])
def message():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        response = bot_service.send_message(data)
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/chats/<user_id>', methods=['GET'])
def chats(user_id):
    try:
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
                     
        response = bot_service.get_user_chats(user_id)
                 
        return jsonify(response)
         
    except Exception as e:
        print(f"Error list chats: {str(e)}")
        return jsonify({"Error": str(e)}), 500

@app.route('/chat_messages/<user_id>/<chat_id>', methods=['GET'])
def chat_messages(user_id, chat_id):
    try:
        if not all([chat_id, user_id]):
            return jsonify({"error": "Chat ID and User ID are required"}), 400
                         
        response = bot_service.get_chat_messages(user_id, chat_id)
                 
        return jsonify(response)
         
    except Exception as e:
        print(f"Error list chats: {str(e)}")
        return jsonify({"Error": str(e)}), 500


@app.route('/upload-image', methods=['POST'])
def upload_image():
   try:
       data = request.json
       if not data or 'image' not in data:
           return jsonify({'error': 'No se envió imagen'}), 400
       
       user_id = data.get('user_id')
       chat_id = data.get('chat_id')
       
       if not all([user_id, chat_id]):
           return jsonify({'error': 'User ID y Chat ID requeridos'}), 400
       
       image_base64 = data['image']
       if ',' in image_base64:
           image_base64 = image_base64.split(',')[1]
       
       image_data = base64.b64decode(image_base64)
       os.makedirs('./uploads', exist_ok=True)
       
       image_path = './uploads/image.png'
       with open(image_path, 'wb') as f:
           f.write(image_data)
       
       message_data = {
           'user_id': user_id,
           'chat_id': chat_id,
           'message': 'image'
       }
       
       response = bot_service.send_message(message_data)
       
       return jsonify(response)
       
   except Exception as e:
       print(f"Error guardando imagen: {str(e)}")
       return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True, port=5000)