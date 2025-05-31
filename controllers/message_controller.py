import json
from odoo import http
from odoo.http import request, Response
from ..services.controller.message_services import MessageService
from ..utils.response.response_builder import ResponseBuilder
from ..services.controller.file_services import FileService
from ..utils.validation.payload_validator import PayloadValidator
from ..utils.log.controller_logger import LoggerController

class MessageMessageController(http.Controller):
    """Controller for handling WhatsApp message operations."""
    
    def __init__(self):
        super(MessageMessageController, self).__init__()
        self.message_service = MessageService()
        self.response_builder = ResponseBuilder()
        self.file_service = FileService()
        self.payload_validator = PayloadValidator()
        self.logger = LoggerController().get_logger("message_controller")
    
    @http.route('/api/message/initial_load', type='http', auth='public', csrf=False)
    def initial_load(self, chat_id):
        """Endpoint for initializing message data load for a WhatsApp user."""
        try:
            self.message_service.initial_load(chat_id)
            return self.response_builder.success('Carga inicial de Mensajes completada.')
        except Exception as e:
            self.logger.error(f"Error al cargar datos iniciales: {e}")
            return self.response_builder.error(str(e))

    @http.route('/api/messages/<int:chat_id>', type='http', auth='public', csrf=False)
    def get_messages(self, chat_id):
        """Retrieves messages for a specific chat."""
        try:
            chat_data, messages_data = self.message_service.get_chat_messages(chat_id)
            return self.response_builder.success_with_data({
                'chat': chat_data,
                'messages': messages_data
            })
        except Exception as e:
            self.logger.error(f"Error al obtener mensajes: {e}")
            chat_info = self.message_service.get_basic_chat_info(chat_id)
            return self.response_builder.error_with_data(
                str(e), 
                {'chat_info': chat_info, 'messages': []}
            )

    @http.route('/api/message/send-sticker', type='http', auth='public', methods=['POST'], csrf=False)
    def send_message_sticker(self):
        """Endpoint for sending a sticker message."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['chat_id', 'sticker_url', 'file_name']
            
            validation_result = self.payload_validator.validate_json_payload(post, required_fields)
            if not validation_result.is_valid:
                return self.response_builder.error(validation_result.error_message)
                
            result = self.message_service.send_sticker(
                post['chat_id'], 
                post['sticker_url'], 
                post['file_name']
            )
            
            if result.success:
                return self.response_builder.success('Mensaje enviado correctamente.')
            else:
                return self.response_builder.error(result.error_message)
                
        except Exception as e:
            self.logger.error(f"Error al enviar sticker: {e}")
            return self.response_builder.error(str(e))
            
    @http.route('/api/message/send', type='http', auth='public', methods=['POST'], csrf=False)
    def send_message(self):
        """Endpoint for sending a text message."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['chat_id', 'message_body']
            
            validation_result = self.payload_validator.validate_json_payload(post, required_fields)
            if not validation_result.is_valid:
                return self.response_builder.error(validation_result.error_message)
                
            result = self.message_service.send_message(
                post['chat_id'], 
                post['message_body']
            )
            
            if result.success:
                return self.response_builder.success('Mensaje enviado correctamente.')
            else:
                return self.response_builder.error(result.error_message)
                
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje: {e}")
            return self.response_builder.error(str(e))
            
    @http.route('/api/message/send-default-messages', type='http', auth='public', methods=['POST'], csrf=False)
    def send_default_message(self):
        """Endpoint for sending a default message."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['chat_id', 'default_id']
            
            validation_result = self.payload_validator.validate_json_payload(post, required_fields)
            if not validation_result.is_valid:
                return self.response_builder.error(validation_result.error_message)
                
            result = self.message_service.send_default_message(
                post['chat_id'], 
                post['default_id']
            )
            
            if result.success:
                return self.response_builder.success('Mensaje enviado correctamente.')
            else:
                return self.response_builder.error(result.error_message)
                
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje predeterminado: {e}")
            return self.response_builder.error(str(e))
            
    @http.route('/api/message/send-product', type='json', auth='public', methods=['POST'], csrf=False)
    def send_product(self):
        """Endpoint for sending a product as a message in a specific chat."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['chat_id', 'product_id']
            
            validation_result = self.payload_validator.validate_json_payload(post, required_fields)
            if not validation_result.is_valid:
                return {'status': 'error', 'message': validation_result.error_message}
                
            result = self.message_service.send_product(
                post['chat_id'], 
                post['product_id']
            )
            
            if result.success:
                return {'status': 'success', 'message': 'Producto enviado correctamente.'}
            else:
                return {'status': 'error', 'message': result.error_message}
                
        except Exception as e:
            self.logger.error(f"Error al enviar producto: {e}")
            return {'status': 'error', 'message': str(e)}

    @http.route('/send_file_path', type='json', auth='user', methods=['POST'])
    def send_file_path(self):
        """Envía un archivo a través de WhatsApp usando una ruta de archivo."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['file_name', 'file_content', 'chatId']
            
            # Validar campos requeridos
            for field in required_fields:
                if not post.get(field):
                    return {
                        'status': 'error', 
                        'message': f'Campo requerido: {field}'
                    }
            
            # Logs para depuración
            self.logger.info(f"Datos recibidos: {post}")
            
            # Usar el servicio para enviar el archivo
            result = self.file_service.send_file_by_path(
                post.get('file_name'),
                post.get('file_content'),
                post.get('chatId'),
                post.get('messageBody', '')
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al enviar archivo: {str(e)}", exc_info=True)
            return {
                'status': 'error', 
                'message': str(e)
            }

    @http.route('/api/message/send-file', type='http', auth='public', methods=['POST'], csrf=False)
    def send_message_file(self):
        """Endpoint para enviar un mensaje con archivo."""
        try:
            uploaded_file = request.httprequest.files.get('file')
            chat_id = request.params.get('chat_id')
            message_body = request.params.get('message_body')

            self.logger.info(f"Recibido chat_id: {chat_id}, archivo: {uploaded_file}, message_body: {message_body}")

            if not chat_id or not uploaded_file or not message_body:
                return self.response_builder.error('Faltan parámetros requeridos.')

            result = self.file_service.send_message_with_file(chat_id, uploaded_file, message_body)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al enviar mensaje con archivo: {e}", exc_info=True)
            return self.response_builder.exception(e)

    @http.route('/api/message/reply', type='http', auth='public', methods=['POST'], csrf=False)
    def reply_message(self):
        """Responde a un mensaje específico."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['message_id', 'reply']

            # Validar campos requeridos
            if not post or not all(field in post for field in required_fields):
                return self.response_builder.error('Faltan parámetros requeridos.')

            message_id = post['message_id']
            reply_text = post['reply']

            result = self.message_service.reply_to_message(message_id, reply_text)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al responder mensaje: {e}", exc_info=True)
            return self.response_builder.exception(e)

    @http.route('/api/message/reply-received', type='http', auth='public', methods=['POST'], csrf=False)
    def reply_message_received(self):
        """Responde a un mensaje recibido usando el ID del chat."""
        try:
            post = request.httprequest.get_json()
            required_fields = ['message_id', 'reply', 'chat_id']

            # Validar campos requeridos
            if not post or not all(field in post for field in required_fields):
                return self.response_builder.error('Faltan parámetros requeridos.')

            message_id = post['message_id']
            reply_text = post['reply']
            chat_id = post['chat_id']

            result = self.message_service.reply_to_received_message(message_id, reply_text, chat_id)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al responder mensaje recibido: {e}", exc_info=True)
            return self.response_builder.exception(e)

    @http.route('/api/message/delete', type='http', auth='public', methods=['POST'], csrf=False)
    def delete_message(self):
        """Elimina un mensaje específico."""
        try:
            post = request.httprequest.get_json()
            if not post or 'message_id' not in post:
                return self.response_builder.error('Falta el parámetro requerido.')

            message_id = post['message_id']
            result = self.message_service.delete_message(message_id)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al eliminar mensaje: {e}", exc_info=True)
            return self.response_builder.exception(e)

    @http.route('/api/message/mark_important', type='http', auth='public', methods=['POST'], csrf=False)
    def mark_important_message(self):
        """Marca un mensaje como importante."""
        try:
            post = request.httprequest.get_json()
            if not post or 'message_id' not in post:
                return self.response_builder.error('Falta el parámetro requerido.')

            message_id = post['message_id']
            result = self.message_service.mark_message_as_important(message_id)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al marcar mensaje como importante: {e}", exc_info=True)
            return self.response_builder.exception(e)

    @http.route('/api/message/unmark_important', type='http', auth='public', methods=['POST'], csrf=False)
    def unmark_important_message(self):
        """Desmarca un mensaje importante."""
        try:
            post = request.httprequest.get_json()
            if not post or 'message_id' not in post:
                return self.response_builder.error('Falta el parámetro requerido.')

            message_id = post['message_id']
            result = self.message_service.unmark_message_as_important(message_id)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al desmarcar mensaje importante: {e}", exc_info=True)
            return self.response_builder.exception(e)

    @http.route('/api/message/edit', type='http', auth='public', methods=['POST'], csrf=False)
    def edit_message(self):
        """Edita el contenido de un mensaje existente."""
        try:
            post = request.httprequest.get_json()
            if not post or 'messageId' not in post or 'newContent' not in post:
                return self.response_builder.error('Faltan parámetros requeridos.')

            message_id = post['messageId']
            new_content = post['newContent']
            
            result = self.message_service.edit_message(message_id, new_content)
            return Response(json.dumps(result), content_type='application/json')
            
        except Exception as e:
            self.logger.error(f"Error al editar mensaje: {e}", exc_info=True)
            return self.response_builder.exception(e)