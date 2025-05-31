from odoo import http
from odoo.http import request
from ..services.controller.chat_services import ChatService
from ..utils.validation.payload_validator import PayloadValidator
from ..utils.log.controller_logger import LoggerController
from ..utils.response.response import ResponseHandler

class MessageChatController(http.Controller):
    """Controlador para manejar las solicitudes de WhatsApp."""
    
    def __init__(self):
        super(MessageChatController, self).__init__()
        self.whatsapp_service = ChatService()
        self.validator = PayloadValidator()
        self.response_handler = ResponseHandler()
        self.logger = LoggerController().get_logger("chat_controller")
    
    @http.route('/api/chat/process_message', type='json', auth='public', csrf=False)
    def process_message(self):
        """Endpoint para procesar mensajes entrantes desde el WebSocket."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['from_serialized', 'timestamp', 'user_phone_number']

            is_valid, error_message = self.validator.validate_payload(post, required_fields)
            if not is_valid:
                return {'status': 'error', 'message': error_message}
            
            # Procesar mensaje a través del servicio
            return self.whatsapp_service.process_message(post)
            
        except Exception as e:
            self.logger.error(f"Error al procesar el mensaje: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/api/chat/update_status', type='json', auth='public', csrf=False)
    def update_chat_status(self):
        """Endpoint para actualizar el estado de un chat."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['chat_id', 'status_chat']

            is_valid, error_message = self.validator.validate_payload(post, required_fields)
            if not is_valid:
                return {'status': 'error', 'message': error_message}
            
            # Actualizar estado a través del servicio
            return self.whatsapp_service.update_chat_status(post, request.env.user.id)
            
        except Exception as e:
            self.logger.error(f"Error al actualizar el estado del chat: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/chat/id', type='json', auth='public', methods=['POST'], csrf=False)
    def get_chat_id(self):
        """
        Endpoint para obtener el ID de un chat basado en parámetros proporcionados.
        
        Returns:
            dict: Respuesta JSON con el estado y datos del chat si se encuentra
        """
        try:
            # Obtener y validar los parámetros de la solicitud
            post = request.httprequest.get_json()
            params = {
                'serialized': post.get('serialized'),
                'user_id': post.get('user_id'),
                'phone_number': post.get('phone_number')
            }
            
            # Validar que al menos un parámetro esté presente
            if not any(params.values()):
                self.logger.warning('No parameters provided for chat ID retrieval.')
                return self.response_handler.build_error_response('No parameters provided')
            
            # Usar el servicio para buscar el chat y contacto
            whatsapp_service = ChatService()
            result = whatsapp_service.find_chat_and_contact(params)
            
            if result['chat_id']:
                self.logger.info(f'Chat found: {result["chat_id"]}')
                return self.response_handler.build_response(result)
            else:
                self.logger.warning('Chat not found with provided parameters.')
                return self.response_handler.build_error_response('Chat not found')
                
        except Exception as e:
            self.logger.exception('An error occurred while retrieving the chat ID.')
            return self.response_handler.build_error_response(str(e))