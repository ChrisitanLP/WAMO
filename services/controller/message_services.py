import os
import requests
import json
from urllib.parse import urlparse
from dataclasses import dataclass
from odoo import http
from odoo.http import request
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig
from ...controllers.encrypted_controller import WhatsappEncryptedController

@dataclass
class ServiceResult:
    """Data class to represent service operation results."""
    success: bool
    error_message: str = None
    data: dict = None

class MessageService:
    """Service class for WhatsApp message operations."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("message_services")
    
    def initial_load(self, chat_id):
        """Initialize data load for a WhatsApp user."""
        whatsapp_message_model = request.env['message_app.message_message']
        whatsapp_message_model.initial_load(chat_id)
        return True
        
    def get_chat_messages(self, chat_id):
        """Get messages for a specific chat with complete information."""
        # Initial load of messages
        self.initial_load(chat_id)
        
        # Get the chat
        chat = request.env['message_app.message_chat'].browse(chat_id)
        
        # Prepare chat data
        chat_data = self._prepare_chat_data(chat)
        
        # Get the messages
        messages = request.env['message_app.message_message'].search([('chat_id', '=', chat_id)])
        messages_data = self._prepare_messages_data(messages)
        
        return chat_data, messages_data
        
    def get_basic_chat_info(self, chat_id):
        """Get basic chat information without messages."""
        chat = request.env['message_app.message_chat'].browse(chat_id)
        return {
            'name': chat.name,
            'id': chat.id,
            'profile_pic_url': chat.profile_pic_url,
            'status': chat.status,
            'assigned_user_id': chat.user_attending_id.id,
        }
        
    def _prepare_chat_data(self, chat):
        """Prepare chat data for API response."""
        member_names = {}
        
        # Check if it's a group chat
        if chat.is_group:
            # Get group members and their phone numbers
            group_members = request.env['message_app.message_group_member'].search([
                ('group_id', '=', chat.group_id.id)
            ])
            member_names = {member.id: member.phone_number for member in group_members}
            
        return {
            'name': chat.name,
            'profile_pic_url': chat.profile_pic_url,
            'status': chat.status,
            'assigned_user_id': chat.user_attending_id.id,
            'user_id': chat.user_id.id,
            'is_group': chat.is_group,
            'member_phones': member_names
        }
        
    def _prepare_messages_data(self, messages):
        """Prepare messages data for API response."""
        return [{
            'id': msg.id,
            'from_user': msg.from_user,
            'serialized': msg.serialized,
            'body': msg.body,
            'type': msg.media_type,
            'from_Me': msg.from_me,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'media_data': msg.media_base64,
            'media_temp_url': msg.media_temp_url,
            'hasQuotedMsg': msg.has_quoted_msg,
            'quoted_id': msg.quoted_serialized,
            'quoted_body': msg.quoted_body,
            'quoted_from_user': msg.quoted_from_user,
            'quoted_to_user': msg.quoted_to_user,
            'quoted_type': msg.quoted_type,
            'latitude': msg.location_latitude,
            'is_starred': msg.is_starred,
            'is_forwarded': msg.is_forwarded,
            'longitude': msg.location_longitude,
            'media_mime_type': msg.mime_type
        } for msg in messages]
        
    def send_sticker(self, chat_id, sticker_url, file_name):
        """Send a sticker message to a chat."""
        try:
            # Get chat information
            chat = self._get_chat(chat_id)
            if not chat:
                return ServiceResult(False, 'Chat no encontrado.')
                
            # Process sticker path
            sticker_path = self._process_sticker_path(sticker_url, file_name)
            
            # Get API URL and prepare data
            api_base_url = self.api_config.get_api_url()
            api_url = f"{api_base_url}/sendSticker"
            
            data = self._prepare_sticker_data(chat, sticker_path)
            
            # Make API request
            response = self._make_api_request(api_url, data)
            return self._process_api_response(response)
            
        except Exception as e:
            self.logger.error(f"Error al enviar sticker: {e}")
            return ServiceResult(False, str(e))
    
    def send_message(self, chat_id, message_body):
        """Send a text message to a chat."""
        try:
            # Get chat information
            chat = self._get_chat(chat_id)
            if not chat:
                return ServiceResult(False, 'Chat no encontrado.')
                
            # Get API URL and prepare data
            api_base_url = self.api_config.get_api_url()
            
            if chat.is_group:
                api_url = f"{api_base_url}/sendGroupMessage"
                data = {
                    'clientId': chat.user_id.connection_id.phone_number,
                    'groupId': chat.group_id.group_number,
                    'mensaje': message_body,
                }
            else:
                api_url = f"{api_base_url}/sendMessage"
                data = {
                    'clientId': chat.user_id.connection_id.phone_number,
                    'tel': chat.phone_number,
                    'mensaje': message_body,
                }
                
            # Log the data for debugging
            self.logger.info(f"Preparando envío de mensaje - Data: {data}")
            
            # Make API request
            response = self._make_api_request(api_url, data)
            return self._process_api_response(response)
            
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")
            return ServiceResult(False, f"Error al enviar mensaje: {str(e)}")
            
    def send_default_message(self, chat_id, default_id):
        """Send a predefined default message to a chat."""
        try:
            # Get chat information
            chat = self._get_chat(chat_id)
            if not chat:
                return ServiceResult(False, 'Chat no encontrado.')
                
            # Get default message
            default = self._get_default_message(default_id)
            if not default:
                return ServiceResult(False, 'Mensaje por defecto no encontrado.')
                
            # Prepare message data based on message type
            message_body, file_path = self._prepare_default_message_data(default)
            
            # Get API URL and prepare request data
            api_base_url = self.api_config.get_api_url()
            api_url, data = self._prepare_default_message_request(chat, message_body, file_path, default.type)
            
            # Make API request
            response = self._make_api_request(api_url, data)
            return self._process_api_response(response)
            
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje predeterminado: {e}")
            return ServiceResult(False, str(e))
            
    def send_product(self, chat_id, product_id):
        """Send product information as a message."""
        try:
            # Get chat information
            chat = self._get_chat(chat_id)
            if not chat:
                return ServiceResult(False, 'Chat no encontrado.')
                
            # Get product
            product = self._get_product(product_id)
            if not product:
                return ServiceResult(False, 'Producto no encontrado.')
                
            # Prepare product message data
            message_body, image_base64 = self._prepare_product_data(product)
            
            # Get API URL and prepare request data
            api_base_url = self.api_config.get_api_url()
            if chat.is_group:
                api_url = f"{api_base_url}/sendGroupProducts"
                data = {
                    'groupId': chat.group_id.group_number,
                    'mensaje': message_body,
                    'imagen': image_base64,
                    'clientId': chat.user_id.connection_id.phone_number
                }
            else:
                api_url = f"{api_base_url}/sendMessageProducts"
                data = {
                    'tel': chat.phone_number,
                    'mensaje': message_body,
                    'imagen': image_base64,
                    'clientId': chat.user_id.connection_id.phone_number
                }
                
            # Make API request
            response = self._make_api_request(api_url, data)
            return self._process_api_response(response)
            
        except Exception as e:
            self.logger.error(f"Error al enviar producto: {e}")
            return ServiceResult(False, str(e))

    def reply_to_message(self, message_id, reply_text):
        """
        Responde a un mensaje específico.
        
        Args:
            message_id (int): ID del mensaje a responder
            reply_text (str): Texto de la respuesta
            
        Returns:
            dict: Resultado de la operación
        """
        message = self._get_message_by_id(message_id)
        if not message:
            return {'status': 'error', 'message': 'Mensaje no encontrado.'}
            
        message_info = self._get_message_info(message)
        
        data = {
            'clientId': message_info['id_client'],
            'tel': message_info['phone_number'],
            'messageId': message_info['id_message'],
            'isGroup': message_info['is_group'],
            'reply': reply_text,
        }
        
        return self.make_api_request('replyMessage', data)
    
    def reply_to_received_message(self, message_id, reply_text, chat_id):
        """
        Responde a un mensaje recibido usando el ID del chat.
        
        Args:
            message_id (str): ID encriptado del mensaje
            reply_text (str): Texto de la respuesta
            chat_id (int): ID del chat
            
        Returns:
            dict: Resultado de la operación
        """
        chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
        if not chat:
            return {'status': 'error', 'message': 'Chat no encontrado.'}
            
        id_message = message_id
        
        data = {
            'clientId': chat.user_id.connection_id.phone_number,
            'tel': chat.phone_number,
            'messageId': id_message,
            'isGroup': chat.is_group,
            'reply': reply_text,
        }
        
        return self.make_api_request('replyMessage', data)
    
    def delete_message(self, message_id):
        """
        Elimina un mensaje específico.
        
        Args:
            message_id (int): ID del mensaje a eliminar
            
        Returns:
            dict: Resultado de la operación
        """
        message = self._get_message_by_id(message_id)
        if not message:
            return {'status': 'error', 'message': 'Mensaje no encontrado.'}
            
        message_info = self._get_message_info(message)
        
        data = {
            'clientId': message_info['id_client'],
            'tel': message_info['phone_number'],
            'messageId': message_info['id_message'],
            'isGroup': message_info['is_group'],
            'forEveryone': True,
        }
        
        return self.make_api_request('deleteMessage', data, method="DELETE")
    
    def mark_message_as_important(self, message_id):
        """
        Marca un mensaje como importante.
        
        Args:
            message_id (int): ID del mensaje
            
        Returns:
            dict: Resultado de la operación
        """
        message = self._get_message_by_id(message_id)
        if not message:
            return {'status': 'error', 'message': 'Mensaje no encontrado.'}
            
        message_info = self._get_message_info(message)
        
        data = {
            'clientId': message_info['id_client'],
            'tel': message_info['phone_number'],
            'messageId': message_info['id_message'],
            'isGroup': message_info['is_group'],
        }
        
        return self.make_api_request('markMessageImportant', data)
    
    def unmark_message_as_important(self, message_id):
        """
        Desmarca un mensaje importante.
        
        Args:
            message_id (int): ID del mensaje
            
        Returns:
            dict: Resultado de la operación
        """
        message = self._get_message_by_id(message_id)
        if not message:
            return {'status': 'error', 'message': 'Mensaje no encontrado.'}
            
        message_info = self._get_message_info(message)
        
        data = {
            'clientId': message_info['id_client'],
            'tel': message_info['phone_number'],
            'messageId': message_info['id_message'],
            'isGroup': message_info['is_group'],
        }
        
        return self.make_api_request('unmarkMessageImportant', data)
    
    def edit_message(self, message_id, new_content):
        """
        Edita el contenido de un mensaje existente.
        
        Args:
            message_id (int): ID del mensaje
            new_content (str): Nuevo contenido del mensaje
            
        Returns:
            dict: Resultado de la operación
        """
        message = self._get_message_by_id(message_id)
        if not message:
            return {'status': 'error', 'message': 'Mensaje no encontrado.'}
            
        message_info = self._get_message_info(message)
        
        data = {
            'clientId': message_info['id_client'],
            'tel': message_info['phone_number'],
            'messageId': message_info['id_message'],
            'isGroup': message_info['is_group'],
            'newContent': new_content
        }
        
        return self.make_api_request('editMessage', data)

    # Helper methods
    def _get_chat(self, chat_id):
        """Get chat by ID."""
        return request.env['message_app.message_chat'].search([('id', '=', chat_id)], limit=1)
        
    def _get_default_message(self, default_id):
        """Get default message by ID."""
        return request.env['message_app.message_default_message'].search([('id', '=', default_id)], limit=1)
        
    def _get_product(self, product_id):
        """Get product by ID."""
        return request.env['product.template'].browse(product_id)

    def _get_message_by_id(self, message_id):
        """Obtiene un mensaje por su ID."""
        message = request.env['whatsapp_message_api.whatsapp_message'].search([('id', '=', message_id)], limit=1)
        if not message:
            return None
        return message

    def _get_message_info(self, message):
        """Extrae la información necesaria del mensaje."""
        return {
            'is_group': message.chat_id.is_group,
            'id_message': message.serialized,
            'phone_number': message.chat_id.phone_number,
            'id_client': message.chat_id.user_id.connection_id.phone_number
        }

    def _get_success_message(self, endpoint):
        """Retorna un mensaje de éxito basado en el endpoint."""
        messages = {
            'replyMessage': 'Mensaje respondido correctamente.',
            'deleteMessage': 'Mensaje eliminado correctamente.',
            'markMessageImportant': 'Mensaje marcado como importante.',
            'unmarkMessageImportant': 'Mensaje desmarcado como importante.',
            'editMessage': 'Mensaje editado exitosamente.'
        }
        return messages.get(endpoint, 'Operación completada con éxito.')
        
    def _process_sticker_path(self, sticker_url, sticker_name):
        """Process sticker URL to get file system path."""
        if sticker_url.startswith('http://') or sticker_url.startswith('https://'):
            parsed_url = urlparse(sticker_url)
            
            # Get base directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            controllers_index = current_dir.find('controllers/')
            
            # Extract base path
            if controllers_index != -1:
                base_dir = current_dir[:controllers_index]
            else:
                base_dir = current_dir
                
            # Create path to sticker file
            relative_path = 'static/src/img/stickers/' + sticker_name
            adjusted_path = os.path.join(base_dir, relative_path)
            
            return os.path.normpath(adjusted_path)
        
        return sticker_url
        
    def _prepare_sticker_data(self, chat, sticker_path):
        """Prepare data for sticker API request."""
        data = {
            'stickerPath': sticker_path,
            'clientId': chat.user_id.connection_id.phone_number,
            'isGroup': chat.is_group,
        }
        
        if chat.is_group:
            data['tel'] = chat.group_id.group_number
        else:
            data['tel'] = chat.phone_number
            
        return data
        
    def _prepare_default_message_data(self, default):
        """Prepare data for default message based on type."""
        message_body = ""
        file_path = None
        
        # Generate message body according to type
        if default.type == 'text':
            message_body = f"*{default.text}*"
        elif default.type == 'location':
            message_body = f"https://www.google.com/maps?q={default.location_latitude},{default.location_longitude}"
        elif default.type in ['document', 'image']:
            file_path = self._process_file_path(default.file_url, default.file_name)
            message_body = default.file_url
        elif default.type == 'web_page':
            message_body = default.web_url
            
        return message_body, file_path
        
    def _process_file_path(self, file_url, file_name):
        """Process file URL to get file system path."""
        if file_url:
            parsed_url = urlparse(file_url)
            
            # Get base directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            controllers_index = current_dir.find('controllers/')
            
            # Extract base path
            if controllers_index != -1:
                base_dir = current_dir[:controllers_index]
            else:
                base_dir = current_dir
                
            # Create path to file
            relative_path = 'static/src/files/' + file_name
            adjusted_path = os.path.join(base_dir, relative_path)
            
            return os.path.normpath(adjusted_path)
            
        return None
        
    def _prepare_default_message_request(self, chat, message_body, file_path, message_type):
        """Prepare API request data for default message."""
        api_base_url = self.api_config.get_api_url()
        is_group = chat.is_group
        
        if file_path and message_type == 'image':
            api_url = f"{api_base_url}/sendImage"
            data = {
                'imagePath': file_path,
                'clientId': chat.user_id.connection_id.phone_number,
                'isGroup': is_group,
            }
            
            if is_group:
                data['tel'] = chat.group_id.group_number
            else:
                data['tel'] = chat.phone_number
                
        else:
            if is_group:
                api_url = f"{api_base_url}/sendGroupMessage"
                data = {
                    'groupId': chat.group_id.group_number,
                    'mensaje': message_body,
                    'clientId': chat.user_id.connection_id.phone_number,
                }
            else:
                api_url = f"{api_base_url}/sendMessage"
                data = {
                    'tel': chat.phone_number,
                    'mensaje': message_body,
                    'clientId': chat.user_id.connection_id.phone_number,
                }
                
        return api_url, data
        
    def _prepare_product_data(self, product):
        """Prepare product data for message."""
        # Format message body
        message_body = f"*Producto:* {product.name}\n*Precio:* ${product.list_price}"
        
        # Get image data
        image_binary = product.image_1920
        image_text = image_binary.decode('utf-8') if image_binary else None
        image_base64 = f"data:image/png;base64,{image_text}" if image_text else None
        
        return message_body, image_base64
        
    def _make_api_request(self, api_url, data):
        """Make HTTP request to external API."""
        try:
            self.logger.info(f"Enviando solicitud a {api_url} con datos: {data}")
            response = requests.post(api_url, json=data)
            self.logger.info(f"Respuesta recibida: Status: {response.status_code}, Contenido: {response.text}")
            return response
        except Exception as e:
            self.logger.error(f"Error al realizar solicitud API: {e}")
            raise e

    def make_api_request(self, endpoint, data, method="POST"):
        """
        Realiza una solicitud a la API externa.
        
        Args:
            endpoint (str): Endpoint de la API
            data (dict): Datos a enviar
            method (str): Método HTTP (POST, DELETE, etc.)
            
        Returns:
            dict: Respuesta formateada
        """
        try:
            api_base_url = self.api_config.get_api_url()
            api_url = f"{api_base_url}/{endpoint}"
            
            self.logger.error(f"Enviando solicitud a {api_url} con datos: {data}")
            
            if method.upper() == "DELETE":
                response = requests.delete(api_url, json=data)
            else:
                response = requests.post(api_url, json=data)
                
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.error(f"Respuesta de la API: {response_data}")
            
            if response_data.get('success'):
                return {
                    'status': 'success',
                    'message': self._get_success_message(endpoint),
                    'data': response_data.get('data', {})
                }
            else:
                return {
                    'status': 'error',
                    'message': response_data.get('message', 'Error desconocido en la API externa.')
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión con la API: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error de conexión con la API: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error al procesar la solicitud: {str(e)}"
            }
        
    def _process_api_response(self, response):
        """Process API response."""
        try:
            response_data = response.json()
            if response.status_code == 200:
                if response_data.get('success'):
                    return ServiceResult(True)
                else:
                    error_msg = response_data.get('message', 'Error sin especificar en la API externa')
                    self.logger.error(f"Error de API (status 200): {error_msg}")
                    return ServiceResult(False, error_msg)
            else:
                error_msg = f"Error en la respuesta de la API externa. Status: {response.status_code}. Detalle: {response.text}"
                self.logger.error(error_msg)
                return ServiceResult(False, error_msg)
        except ValueError as e:
            error_msg = f"Error al procesar respuesta JSON. Status: {response.status_code}. Contenido: {response.text}"
            self.logger.error(error_msg)
            return ServiceResult(False, error_msg)
        except Exception as e:
            error_msg = f"Error inesperado al procesar respuesta: {str(e)}"
            self.logger.error(error_msg)
            return ServiceResult(False, error_msg)
