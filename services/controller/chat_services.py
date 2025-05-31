import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from odoo.http import request
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class ChatService:
    """Servicio para manejar la lógica de negocio de WhatsApp."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("chat_services")
    
    def process_message(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje entrante de WhatsApp.
        
        Args:
            post_data (dict): Datos del mensaje recibido
            
        Returns:
            dict: Resultado del procesamiento
        """
        serialized = post_data['from_serialized']
        timestamp = post_data['timestamp']
        user_number = post_data['user_phone_number']
        body = post_data.get('body', "")
        message_type = post_data.get('messageType', "")
        name_message = post_data.get('name_message', "")

        # Procesar información del chat
        is_group, phone_number = self._extract_phone_number(serialized)
        
        self.logger.info(
            "Datos recibidos: serialized=%s, message_type=%s, timestamp=%s, user_number=%s, name=%s, phone=%s", 
            serialized, message_type, timestamp, user_number, name_message, phone_number
        )

        # Validar datos mínimos requeridos
        if not serialized or not timestamp:
            return {'status': 'error', 'message': 'Faltan parámetros necesarios.'}

        # Buscar usuario y chat
        user, chat = self._find_user_and_chat(user_number, serialized, phone_number)
        user_id = user.id if user else None

        # Actualizar o crear chat según corresponda
        if chat:
            result = self._update_existing_chat(chat, body, message_type, timestamp)
        else:
            result = self._create_new_chat(
                serialized, phone_number, name_message, user_id, 
                body, message_type, timestamp, is_group
            )

        return {
            'status': 'success',
            'message': 'Mensaje procesado correctamente.',
            **result
        }
    
    def update_chat_status(self, post_data: Dict[str, Any], current_user_id: int) -> Dict[str, Any]:
        """
        Actualiza el estado de un chat.
        
        Args:
            post_data (dict): Datos para actualizar el chat
            current_user_id (int): ID del usuario actual
            
        Returns:
            dict: Resultado de la actualización
        """
        chat_id = post_data['chat_id']
        status_chat = post_data['status_chat']

        chat = request.env['message_app.message_chat'].browse(int(chat_id))
        
        if not chat.exists():
            return {'status': 'error', 'message': 'Chat no encontrado.'}
            
        # Aplicar reglas de negocio según el estado solicitado
        if status_chat == 'atendiendo':
            return self._handle_attending_status(chat, current_user_id)
        elif status_chat == 'pendiente':
            return self._handle_pending_status(chat)
        elif status_chat == 'atendido':
            return self._handle_attended_status(chat)
        else:
            return {'status': 'error', 'message': 'Estado no válido.'}
    
    def _extract_phone_number(self, serialized: str) -> Tuple[bool, str]:
        """
        Extrae el número de teléfono del serialized y determina si es un grupo.
        
        Args:
            serialized (str): ID serializado del chat
            
        Returns:
            tuple: (is_group, phone_number)
        """
        if '@g.us' in serialized:
            return True, re.sub(r'@g\.us$', '', serialized)
        else:
            return False, re.sub(r'@c\.us$', '', serialized)
    
    def _find_user_and_chat(self, user_number: str, serialized: str, phone_number: str) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Busca el usuario y chat correspondientes.
        
        Args:
            user_number (str): Número de teléfono del usuario
            serialized (str): ID serializado del chat
            phone_number (str): Número de teléfono extraído
            
        Returns:
            tuple: (user, chat)
        """
        user = request.env['message_app.message_user'].search(
            [('phone_number', '=', user_number)], limit=1
        )
        
        if not user:
            return None, None
            
        domain = [
            ('serialized', '=', serialized),
            ('user_id', '=', user.id),
            ('phone_number', '=', phone_number)
        ]
        
        chat = request.env['message_app.message_chat'].search(domain, limit=1)
        return user, chat
    
    def _update_existing_chat(self, chat: Any, body: str, message_type: str, timestamp: int) -> Dict[str, Any]:
        """
        Actualiza un chat existente.
        
        Args:
            chat: Objeto de chat existente
            body (str): Cuerpo del mensaje
            message_type (str): Tipo de mensaje
            timestamp (int): Timestamp del mensaje
            
        Returns:
            dict: Datos actualizados del chat
        """
        unread_count = chat.unread_count + 1
        
        chat.write({
            'last_message_body': body,
            'last_message_type': message_type,
            'unread_count': unread_count,
            'timestamp': datetime.utcfromtimestamp(timestamp)
        })
        
        return {
            'chat_id': chat.id, 
            'unread_count': unread_count,
            'name': chat.name,
            'profile': chat.profile_pic_url,
            'status_chat': chat.status,
            'user_attending_id': chat.user_attending_id.id if chat.user_attending_id else False,
            'user_id': chat.user_id.id if chat.user_id else False
        }
    
    def _create_new_chat(self, serialized: str, phone_number: str, name: str, user_id: Optional[int], 
                         body: str, message_type: str, timestamp: int, is_group: bool) -> Dict[str, Any]:
        """
        Crea un nuevo chat.
        
        Args:
            serialized (str): ID serializado del chat
            phone_number (str): Número de teléfono
            name (str): Nombre del chat
            user_id (int): ID del usuario
            body (str): Cuerpo del mensaje
            message_type (str): Tipo de mensaje
            timestamp (int): Timestamp del mensaje
            is_group (bool): Indica si es un grupo
            
        Returns:
            dict: Datos del nuevo chat
        """
        new_chat = request.env['message_app.message_chat'].create({
            'serialized': serialized,
            'phone_number': phone_number,
            'name': name,
            'user_id': user_id,
            'last_message_body': body,
            'last_message_type': message_type,
            'unread_count': 1,
            'timestamp': datetime.utcfromtimestamp(timestamp),
            'status': 'pendiente',
            'is_group': is_group
        })
        
        return {
            'chat_id': new_chat.id, 
            'unread_count': new_chat.unread_count,
            'name': name,
            'profile': new_chat.profile_pic_url,
            'status_chat': new_chat.status,
            'user_attending_id': False,
            'user_id': user_id
        }
    
    def _handle_attending_status(self, chat: Any, current_user_id: int) -> Dict[str, Any]:
        """
        Maneja la transición al estado 'atendiendo'.
        
        Args:
            chat: Objeto de chat
            current_user_id (int): ID del usuario actual
            
        Returns:
            dict: Resultado de la operación
        """
        # Verifica si el chat ya está siendo atendido por otro usuario
        if chat.user_attending_id and chat.user_attending_id.id != current_user_id:
            return {
                'status': 'error', 
                'message': 'Este chat ya está siendo atendido por otro usuario.'
            }

        # Actualiza el estado del chat y asigna el usuario que lo está atendiendo
        chat.write({
            'status': 'atendiendo',
            'user_attending_id': current_user_id
        })
        
        return self._get_chat_update_response(chat)
    
    def _handle_pending_status(self, chat: Any) -> Dict[str, Any]:
        """
        Maneja la transición al estado 'pendiente'.
        
        Args:
            chat: Objeto de chat
            
        Returns:
            dict: Resultado de la operación
        """
        chat.write({
            'status': 'pendiente',
            'user_attending_id': False
        })
        
        return self._get_chat_update_response(chat)
    
    def _handle_attended_status(self, chat: Any) -> Dict[str, Any]:
        """
        Maneja la transición al estado 'atendido'.
        
        Args:
            chat: Objeto de chat
            
        Returns:
            dict: Resultado de la operación
        """
        chat.write({
            'status': 'atendido',
            'unread_count': 0,
            'user_attending_id': False
        })
        
        return self._get_chat_update_response(chat)
    
    def _get_chat_update_response(self, chat: Any) -> Dict[str, Any]:
        """
        Genera una respuesta estándar para actualizaciones de estado de chat.
        
        Args:
            chat: Objeto de chat
            
        Returns:
            dict: Respuesta estándar
        """
        return {
            'status': 'success', 
            'message': 'Estado del chat actualizado.', 
            'last_message_body': chat.last_message_body, 
            'unread_count': chat.unread_count, 
            'last_message_type': chat.last_message_type
        }

    def find_chat_and_contact(self, params: Dict[str, Any]) -> Dict[str, Optional[int]]:
        """
        Busca un chat y contacto basado en los parámetros proporcionados.
        
        Args:
            params (Dict[str, Any]): Diccionario con serialized, user_id y phone_number
            
        Returns:
            Dict[str, Optional[int]]: Resultado con chat_id y contact_id
        """
        # Crear un dominio con los parámetros no vacíos
        domain = []
        
        if params['serialized']:
            domain.append(('serialized', '=', params['serialized']))
        if params['user_id']:
            domain.append(('user_id', '=', params['user_id']))
        if params['phone_number']:
            domain.append(('phone_number', '=', params['phone_number']))
            
        # Buscar chat y contacto sólo si hay parámetros en el dominio
        chat_id = None
        contact_id = None
        
        if domain:
            chat = request.env['message_app.message_chat'].search(domain, limit=1)
            chat_id = chat.id if chat else None
            
            contact = request.env['message_app.message_contact'].search(domain, limit=1)
            contact_id = contact.id if contact else None
        
        return {
            'chat_id': chat_id,
            'contact_id': contact_id
        }