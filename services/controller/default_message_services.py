from typing import List, Dict, Any
from odoo.exceptions import UserError
from odoo.http import request
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class DefaultMessageService:
    def __init__(self, env=None):
        self.env = env or request.env
        self.logger = ExtraLoggerConfig().get_logger("sticker_storage")
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Obtiene todos los mensajes activos"""
        try:
            messages = list(self.env['message_app.message_default_message'].search([]))
            return self._format_messages(messages)
        except Exception as e:
            self.logger.error(f"Error fetching messages: {str(e)}")
            raise

    def get_message_by_id(self, message_id: int) -> Dict[str, Any]:
        """Obtiene un mensaje específico por ID"""
        message = self.env['message_app.message_default_message'].browse(message_id)
        if not message.exists():
            raise UserError("El mensaje no existe")
        return self._format_message(message)

    def create_default_messages(self) -> List[Dict[str, Any]]:
        """Crea un nuevo mensaje"""
        try:
            messages = self.env['message_app.message_default_message'].create_default_messages()
        
            # Si create_default_messages() devuelve una lista de registros, formateamos la lista
            if isinstance(messages, list):
                return self._format_messages(messages)  
            
            # Si devuelve un solo registro, lo convertimos en una lista
            return [self._format_message(messages)]

        except Exception as e:
            self.logger.error(f"Error creating message: {str(e)}")
            raise

    def update_message(self, message_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un mensaje existente"""
        message = self.env['message_app.message_default_message'].browse(message_id)
        if not message.exists():
            raise UserError("El mensaje con el ID dado no existe.")
        message.write(data)
        return self._format_message(message)

    def delete_message(self, message_id: int, env=None) -> None:
        """Elimina un mensaje"""
        env = env or request.env
        try:
            message = env['message_app.message_default_message'].browse(message_id)
            if not message.exists():
                raise UserError("El mensaje con el ID dado no existe.")
            message.unlink()
        except Exception as e:
            self.logger.error(f"Error al eliminar mensaje {message_id}: {str(e)}")
            raise

    def create_message(self, data: Dict[str, Any], env=None) -> Dict[str, Any]:
        """Crea un nuevo mensaje"""
        env = env or request.env
        try:
            # Create the message
            message = env['message_app.message_default_message'].create(data)
            
            # Immediately read the data within the same transaction
            message_data = message.read(['id', 'name', 'type', 'text', 'location', 
                            'location_latitude', 'location_longitude', 'code', 
                            'file_url', 'file_name', 'web_url', 'active'])[0]
            
            return message_data
        except Exception as e:
            self.logger.error(f"Error creating message: {str(e)}")
            raise

    def _format_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """Formatea una lista de mensajes para la respuesta"""
        result = []
        for message in messages:
            try:
                result.append(self._format_message(message))
            except Exception as e:
                self.logger.error(f"Error formatting message: {str(e)}")
        return result

    def _format_message(self, message: Any) -> Dict[str, Any]:
        """Formatea un mensaje individual para la respuesta"""
        try:
            return message.read(['id', 'name', 'type', 'text', 'location', 
                           'location_latitude', 'location_longitude', 'code', 
                           'file_url', 'file_name', 'web_url', 'active'])[0]
        except Exception as e:
            self.logger.error(f"Error reading message data: {str(e)}")
            # Return basic data as fallback
            return {
                'id': message.id if hasattr(message, 'id') else None,
                'name': message.name if hasattr(message, 'name') else '',
                'type': message.type if hasattr(message, 'type') else '',
                'text': message.text if hasattr(message, 'text') else '',
            }