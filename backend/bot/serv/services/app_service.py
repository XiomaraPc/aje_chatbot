from config.logger_config import get_logger
from services.agent_service import AJEChatbot
from services.memory_service import MemoryService

log = get_logger()

class CHATBOT:
    def __init__(self):
        self.memory_service = MemoryService()

    def start_chat(self, user_id: str):
        """Inicia un nuevo chat y devuelve el chat_id generado"""
        try:
            chat_id = self.memory_service.create_chat_id()
            
            success = self.memory_service.save_chat_info(user_id, chat_id)
            
            if success:
                return {
                    "message": "Chat iniciado exitosamente",
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "date_creation": chat_id,
                    "status": "success"
                }
            else:
                return {"error": "Error creando chat", "status": "error"}

        except Exception as e:
            log.error("Error al iniciar el chat: %s", str(e))
            return {"error": "Error al iniciar el chat", "status": "error"}

    def send_message(self, data):
        """Envía mensaje al chatbot y guarda la conversación"""
        try:
            message = data.get("message")
            chat_id = data.get("chat_id")
            user_id = data.get("user_id")
            
            if not all([message, chat_id, user_id]):
                return {"error": "Faltan parámetros requeridos", "status": "error"}
            
            log.info("Procesando respuesta ...")
            bot = AJEChatbot(user_id=user_id, chat_id=chat_id)
            bot_response = bot.process_message(message)
            # assistant_response = bot_response.get('respuesta')
            
            self.memory_service.save_message(user_id, chat_id, message, bot_response)
            
            return {
                "usuario": user_id,
                "chat_id": chat_id,
                "response": bot_response,
                "status": "success"
            }
        
        except Exception as e:
            log.error("Error al enviar mensaje: %s", str(e))
            return {"error": "Error procesando mensaje", "status": "error"}
        
    def get_user_chats(self, user_id: str) -> list:
        try:
            items = self.memory_service.get_user_chats(user_id)
            return items

        except Exception as e:
            log.info("Error obteniendo chats del usuario: %s", str(e))
            return []
        
    def get_chat_messages(self, user_id: str, chat_id: str) -> list:
        try:
            messages = self.memory_service.get_chat_messages(user_id, chat_id)
            return messages

        except Exception as e:
            log.info("Error obteniendo mensajes del chat: %s", str(e))
            return []
        
    def get_titulo(self, user_id: str, chat_id: str) -> str:
        try:
            titulo = self.memory_service.get_titulo(user_id, chat_id)
            return titulo

        except Exception as e:
            log.info("Error obteniendo titulo: %s", str(e))
            return ""

    def delete_chat(self, user_id: str, chat_id: str) -> dict:
        try:
            success = self.memory_service.clear_chat_history(user_id, chat_id)
            
            if success:
                return {
                    "message": "Chat eliminado exitosamente",
                    "status": "success"
                }
            else:
                return {"error": "No se pudo eliminar el chat", "status": "error"}

        except Exception as e:
            log.error("Error eliminando chat: %s", str(e))
            return {"error": "Error eliminando chat", "status": "error"}