from odoo import http
from odoo.http import request
from ..services.controller.general_services import GeneralService
from ..utils.response.response_builder import ResponseBuilder
from ..utils.log.controller_logger import LoggerController

class MessageGeneralController(http.Controller):
    """Controlador principal para gestionar las operaciones de chats y contactos de WhatsApp."""

    def __init__(self):
        super(MessageGeneralController, self).__init__()
        self.general_service = GeneralService()
        self.response_builder = ResponseBuilder()
        self.logger = LoggerController().get_logger("general_controller")

    @http.route('/whatsapp/messages_app', auth='public', website=True)
    def list_combined_chats_contacts(self, **kwargs):
        """
        Endpoint para mostrar la plantilla inicial con chats y contactos de WhatsApp.
        
        Returns:
            http.Response: Plantilla renderizada con datos de chats y contactos
        """
        try:
            # Llamadas a los métodos de carga inicial a través del servicio

            self.general_service.load_initial_data()

            current_user_id = request.env.user.id

            # Obtener chats ordenados por timestamp mediante el servicio
            chats = self.general_service.get_user_chats(current_user_id)
            contacts = self.general_service.get_contacts()

            # Renderizar la plantilla principal
            return request.render('message_app.chats_and_contacts_template', {
                'chats': chats,
                'contacts': contacts
            })
        except Exception as e:
            self.logger.error(f"Error al cargar datos combinados de chats y contactos: {e}")
            return request.render('message_app.error_page_message', {
                'error_message': str(e)
            })

    @http.route('/api/whatsapp/<template_name>', auth='public', website=True)
    def get_template(self, template_name, **kwargs):
        """
        Endpoint para cargar una plantilla específica.
        
        Args:
            template_name (str): Nombre de la plantilla a cargar
            
        Returns:
            http.Response: Plantilla renderizada con datos correspondientes
        """
        try:
            # Utilizar el servicio para obtener los datos según la plantilla
            template_data = self.general_service.get_template_data(template_name)
            
            if not template_data:
                return request.render('http_routing.404')

            # Renderizar la plantilla con los datos
            return request.render(f'message_app.{template_name}', template_data)
        except Exception as e:
            self.logger.error(f"Error al cargar la plantilla {template_name}: {e}")
            return request.render('http_routing.404')

    @http.route('/api/chat/initial_load', type='http', auth='public')
    def initial_load(self):
        """
        Endpoint para iniciar la carga inicial de datos del usuario de WhatsApp.
        
        Returns:
            Response: Resultado de la operación en formato JSON
        """
        try:
            # Usar el servicio para la carga inicial
            self.general_service.load_initial_chats()
            
            # Construir respuesta utilizando el ResponseBuilder
            return self.response_builder.build_success_response(
                message='Carga inicial de CHATS completada.'
            )
        except Exception as e:
            self.logger.error(f"Error al cargar datos iniciales: {e}")
            return self.response_builder.build_error_response(
                message=str(e),
                status_code=500
            )

    @http.route('/session_id', type='http', auth='public', methods=['GET'], csrf=False)
    def get_session_id(self):
        """
        Obtiene el ID de sesión del usuario actual.
        
        Returns:
            Response: Respuesta HTTP con el ID de sesión.
        """
        try:
            session_id = request.env.user.id
            return self.response_builder.success(data={"session": session_id})
        except Exception as e:
            self.logger.error("Error al obtener ID de sesión", exc_info=True)
            return self.response_builder.error("Error al obtener la sesión", status_code=500)
    
    @http.route('/whatsapp/menu_opciones', auth='public', website=True)
    def show_custom_landing_page(self, **kwargs):
        """Display custom landing page."""
        return request.render('message_app.landing_page')