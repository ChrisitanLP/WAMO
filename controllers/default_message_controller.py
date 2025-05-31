from odoo import http
import base64
from odoo.http import request, Response
from ..services.controller.default_message_services import DefaultMessageService
from ..services.controller.file_services import FileService
from ..utils.response.response import ResponseHandler
from ..utils.validation.request_validator import RequestValidator
from ..utils.log.controller_logger import LoggerController

class MessageDefaultMessageController(http.Controller):
    def __init__(self):
        super().__init__()
        self.message_service = DefaultMessageService()
        self.file_service = FileService()
        self.response_handler = ResponseHandler()
        self.validator = RequestValidator()
        self.logger = LoggerController().get_logger("default_message_controller")

    @http.route('/api/default_message', type='http', auth='public', methods=['GET'], csrf=False)
    def list_messages(self):
        """Obtiene la lista de mensajes por defecto"""
        try:
            messages = self.message_service.get_all_messages()

            for message in messages:
                if message.get('file_url'):
                    if isinstance(message['file_url'], str):
                        file_data = message['file_url'].encode('utf-8')
                    else:
                        file_data = message['file_url']
                    message['file_url'] = base64.b64encode(file_data).decode('utf-8')

            return self.response_handler.success_response({"data": messages})
        except Exception as e:
            self.logger.error(f"Error listing messages: {str(e)}")
            return self.response_handler.error_response(str(e))

    @http.route('/api/default_message/<int:message_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_message(self, message_id):
        """Obtiene un mensaje específico por ID"""
        try:
            message = self.message_service.get_message_by_id(message_id)
            return self.response_handler.success_response(message)
        except Exception as e:
            self.logger.error(f"Error getting message {message_id}: {str(e)}")
            return self.response_handler.error_response(str(e), 404 if "no existe" in str(e).lower() else 500)

    @http.route('/api/default_message/update/<int:message_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_message(self, message_id, **kwargs):
        """Actualiza un mensaje existente"""
        try:
            self.validator.validate_update_message_request(kwargs)
            message = self.message_service.update_message(message_id, kwargs)
            return self.response_handler.success_response({
                'message': 'Mensaje actualizado exitosamente',
                'data': message
            })
        except Exception as e:
            self.logger.error(f"Error updating message {message_id}: {str(e)}")
            return self.response_handler.error_response(str(e))

    @http.route('/api/default_message/delete/<int:message_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_message(self, message_id):
        """Elimina un mensaje existente"""
        try:
            # Pasar el entorno actual
            self.message_service.delete_message(message_id, request.env)
            return self.response_handler.success_response({
                'message': 'Mensaje eliminado exitosamente'
            })
        except Exception as e:
            self.logger.error(f"Error deleting message {message_id}: {str(e)}")
            return self.response_handler.error_response(str(e))

    @http.route('/api/default_message/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_message(self, **kwargs):
        """Crea un nuevo mensaje por defecto"""
        try:
            # Validar request
            self.validator.validate_create_message_request(kwargs)
            
            # Procesar archivo si existe
            file_data = request.httprequest.files.get('file')
            if file_data:
                file_url = self.file_service.save_file(file_data, kwargs.get('file_name'))
                kwargs['file_url'] = file_url
            
            # Crear mensaje y obtener los datos
            message_data = self.message_service.create_message(kwargs, request.env)
            
            # Return success response with the created message
            return self.response_handler.success_response({
                'message': 'Mensaje creado exitosamente',
                'data': message_data,
                'messages': [message_data]
            })
        except Exception as e:
            self.logger.error(f"Error creating message: {str(e)}")
            return self.response_handler.error_response(str(e))

    @http.route('/api/default_message/create_default', type='http', auth='public', methods=['POST'], csrf=False)
    def create_default_messages(self):
        """Crea mensajes por defecto"""
        try:
            self.message_service.create_default_messages()
            return self.response_handler.success_response({
                'message': 'Mensajes por defecto creados exitosamente'
            })
        except Exception as e:
            self.logger.error(f"Error creating default messages: {str(e)}")
            return self.response_handler.error_response(str(e))

    @http.route('/default_messages', type='http', auth='public', website=True)
    def default_messages_page(self):
        """Renderiza la página de mensajes por defecto"""
        try:
            messages = self.message_service.get_all_messages()
            return request.render('message_app.default_messages_template', {
                'default_messages': messages
            })
        except Exception as e:
            self.logger.error(f"Error rendering messages page: {str(e)}")
            return request.render('message_app.default_messages_template')