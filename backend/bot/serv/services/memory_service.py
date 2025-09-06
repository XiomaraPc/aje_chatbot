# services/memory_service.py
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
from repositories.data_repository import DataRepository
from config.logger_config import get_logger

load_dotenv()
log = get_logger()

class MemoryService:
    def __init__(self):
        self.data_repo = DataRepository()
        self.table_name = os.getenv('TABLE_NAME')
        self.dynamodb = self.data_repo.dynamodb_cliente()
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_chat_id(self) -> str:
        return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    def save_chat_info(self, user_id: str, chat_id: str, titulo: str = ""):
        try:
            item = {
                'pk': f'usr#{user_id}',
                'sk': f'cha#{chat_id}',
                'titulo': titulo,
                'created_at': chat_id
            }
            
            self.table.put_item(Item=item)
            log.info(f"Chat creado: usr#{user_id} - cha#{chat_id}")
            return True
            
        except Exception as e:
            log.error(f"Error creando chat: {str(e)}")
            return False

    def save_message(self, user_id: str, chat_id: str, human_message: str, assistant_response: str):
        try:
            timestamp = datetime.now().isoformat()
            pk = f"usr#{user_id}cha#{chat_id}msg#"
            
            item = {
                'pk': pk,
                'sk': timestamp,
                'human': human_message,
                'ai': assistant_response
            }
            
            self.table.put_item(Item=item)
            log.info(f"Mensaje guardado: {pk}")
            return True
            
        except Exception as e:
            log.error(f"Error guardando mensaje: {str(e)}")
            return False

    def get_user_chats(self, user_id: str) -> list:
        try:
            response = self.table.query(
                KeyConditionExpression="pk = :pk_value AND begins_with(sk, :sk_prefix)",
                ExpressionAttributeValues={
                    ":pk_value": f"usr#{user_id}",
                    ":sk_prefix": "cha#",
                },
                ScanIndexForward=False,
            )

            items = response.get("Items", [])
            return items

        except Exception as e:
            log.info("Error obteniendo chats del usuario: %s", str(e))
            return []

    def get_chat_messages(self, user_id: str, chat_id: str) -> list:
        """Obtiene todos los mensajes de un chat específico."""
        try:
            pk = f"usr#{user_id}cha#{chat_id}msg#"

            response = self.table.query(
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": pk},
                ScanIndexForward=True,
            )

            messages = []
            for item in response.get("Items", []):
                message = {
                    "timestamp": item.get("sk"),
                    "human": item.get("human", ""),
                    "ai": item.get("ai", ""),
                }
                messages.append(message)

            return messages

        except Exception as e:
            log.info("Error obteniendo mensajes del chat: %s", str(e))
            return []

    def get_titulo(self, user_id: str, chat_id: str) -> str:
        """Obtiene el titulo guardado de un chat."""
        try:
            response = self.table.get_item(
                Key={"pk": f"usr#{user_id}", "sk": f"cha#{chat_id}"}
            )

            item = response.get("Item", {})
            titulo = {"titulo": item.get("titulo", "")}
            return titulo

        except Exception as e:
            log.info("Error obteniendo titulo: %s", str(e))
            return ""

    def clear_chat_history(self, user_id: str, chat_id: str) -> bool:
        """Elimina todo el historial de un chat"""
        try:
            # Eliminar mensajes
            pk = f"usr#{user_id}cha#{chat_id}msg#"
            response = self.table.query(
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": pk}
            )
            
            with self.table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(
                        Key={'pk': item['pk'], 'sk': item['sk']}
                    )
            
            # Eliminar chat info
            self.table.delete_item(
                Key={'pk': f'usr#{user_id}', 'sk': f'cha#{chat_id}'}
            )
            
            log.info(f"Chat eliminado: usr#{user_id}cha#{chat_id}")
            return True
            
        except Exception as e:
            log.error(f"Error eliminando chat: {str(e)}")
            return False