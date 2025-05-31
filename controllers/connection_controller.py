from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from ..services.model.client_services import ClientService
from ..services.model.connection_services import ConnectionService
from ..utils.response.response import ResponseHandler
from ..utils.log.controller_logger import LoggerController

class MessageConnectionController(http.Controller):
    """Controller for handling WhatsApp related operations."""
    
    def __init__(self):
        super().__init__()
        self.whatsapp_service = ClientService()
        self.response_handler = ResponseHandler()
        self.logger = LoggerController().get_logger("connection_controller")

    @http.route('/whatsapp/connections', auth='user', type='http', website=True)
    def list_connections(self, **kwargs):
        """List all WhatsApp connections with proper access control."""
        try:
            is_admin = request.env.user.has_group('base.group_system') or request.env.user.has_group('base.group_erp_manager')
        
            if not is_admin:
                 return request.render('message_app.landing_page', {
                    'show_admin_alert': True
                })

            service = ConnectionService(request.env)
            connections = service.get_all_connections(as_dict=False)
            return request.render('message_app.authentication_app', {
                'connections': connections
            })
        except ValidationError as e:
            return request.render('message_app.landing_page')
        except Exception as e:
            self.logger.error("Error loading WhatsApp connections: %s", str(e))
            return request.render('http_routing.404')

    @http.route('/message_app/landing', auth='public', type='http', website=True)
    def landing_page_with_params(self, **kwargs):
        """Landing page que puede mostrar mensajes de error."""
        return request.render('message_app.landing_page', {
            'show_admin_error': 'error' in kwargs and kwargs['error'] == 'admin_required'
        })

    @http.route('/api/connection/add', type='http', auth='user', csrf=False, methods=['POST'])
    def add_connection(self, **kwargs):
        """
        Add a new WhatsApp connection.
        
        Endpoint for creating a new connection with external API registration.
        """
        connection_service = ConnectionService(request.env)

        try:
            # 1. Validar y preparar los datos de la conexión
            connection_data = connection_service.prepare_connection_data(kwargs)
            
            # 2. Registrar el cliente en la API externa 
            self.whatsapp_service.register_client(connection_data['phone_number'])
            
            # 3. Crear el registro en Odoo
            connection = connection_service.create_connection(connection_data)
            
            # Return successful response
            return self.response_handler.success({
                'success': True,
                'message': 'Conexión agregada correctamente',
                'connection': {
                    'id': connection.id,
                    'name': connection.name,
                    'phone_number': connection.phone_number,
                    'color': connection.color
                }
            })
        
        except (ValidationError, UserError) as e:
            # Handle validation and user-related errors
            self.logger.error(f"Validation error in add_connection: {str(e)}")
            return self.response_handler.bad_request(str(e))
        
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error in add_connection: {str(e)}")
            return self.response_handler.error("An unexpected error occurred")

    @http.route('/api/connection/delete/<int:connection_id>', type='http', auth='user', methods=['POST'], csrf=False)
    def delete_connection(self, connection_id: int):
        """
        Delete a WhatsApp connection.
        
        Endpoint for removing a connection and notifying external API.
        """
        connection_service = ConnectionService(request.env)

        try:
            # Find the connection
            connection_model = request.env['message_app.message_connection'].sudo()
            connection = connection_model.browse(connection_id)
            
            if not connection.exists():
                return self.response_handler.not_found("Connection not found")
            
            # Remove client from external WhatsApp API
            # self.whatsapp_service.remove_client(connection.phone_number)
            
            # Delete connection in Odoo
            connection_service.delete_connection(connection_id)
            
            # Return successful response
            return self.response_handler.success({'message': 'Connection deleted successfully'})
        
        except (ValidationError, UserError) as e:
            # Handle validation and user-related errors
            self.logger.error(f"Validation error in delete_connection: {str(e)}")
            return self.response_handler.bad_request(str(e))
        
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error in delete_connection: {str(e)}")
            return self.response_handler.error("An unexpected error occurred")