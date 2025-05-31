import requests
from odoo.exceptions import UserError
from typing import List, Dict, Any
from ...utils.response.requests import get_request
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class MessageService:
    def __init__(self, env):
        self.env = env
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("message_services")

    def get_chat_messages(self, chat):
        """Obtiene los mensajes de un chat según su tipo (grupo o individual)"""
        if chat.is_group:
            return self.get_chat_messages_group(
                chat.user_id.connection_id.phone_number, 
                chat.group_id.group_number
            )
        else:
            return self.get_chat_messages_individual(
                chat.phone_number, 
                chat.user_id.phone_number
            )

    def get_chat_messages_individual(self, phone_number, client_id):
        """Obtiene los mensajes de un chat individual"""
        try:
            api_url = self.api_config.get_api_url()
            response = get_request(f'{api_url}/chatMessages/{client_id}/{phone_number}')
            
            if not response:
                self.logger.error("No se recibió respuesta de la API")
                return []
                
            if response.status_code != 200:
                self.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                return []
                
            messages = response.json().get('messages', [])
            self.logger.info(f"Se obtuvieron {len(messages)} mensajes del chat individual")
            return messages
        except Exception as e:
            self.logger.error(f"Error al obtener mensajes del chat individual: {e}")
            return []
    
    def get_chat_messages_group(self, phone_number, group_id):
        """Obtiene los mensajes de un chat grupal"""
        try:
            api_url = self.api_config.get_api_url()
            response = get_request(f'{api_url}/chatGroupMessages/{phone_number}/{group_id}')
            
            if not response:
                self.logger.error("No se recibió respuesta de la API")
                return []
                
            if response.status_code != 200:
                self.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                return []
                
            messages = response.json().get('messages', [])
            self.logger.info(f"Se obtuvieron {len(messages)} mensajes del chat grupal")
            return messages
        except Exception as e:
            self.logger.error(f"Error al obtener mensajes del chat grupal: {e}")
            return []
    