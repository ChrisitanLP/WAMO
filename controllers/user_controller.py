from odoo import http
from odoo.http import request
from ..services.controller.user_services import UserService
from ..utils.response.response_builder import ResponseBuilder
from ..utils.log.controller_logger import LoggerController

class MessageUserController(http.Controller):
    """
    Controlador que maneja las peticiones HTTP relacionadas con usuarios de WhatsApp.
    """

    def __init__(self):
        self.user_service = UserService()
        self.response_builder = ResponseBuilder()
        self.logger = LoggerController().get_logger("user_controller")

    @http.route('/api/user/initial_load', type='http', auth='public', methods=['POST'], csrf=False)
    def initial_load(self):
        """
        Endpoint para iniciar la carga inicial de datos del usuario de WhatsApp.
        
        Returns:
            Response: Respuesta HTTP con el resultado de la operación.
        """
        try:
            self.logger.info("Iniciando carga inicial de usuarios de WhatsApp")
            self.user_service.initial_load()
            return self.response_builder.success("Carga inicial de Usuarios completada.")
        except Exception as e:
            self.logger.error("Error al cargar datos iniciales", exc_info=True)
            return self.response_builder.error(f"Error al cargar datos iniciales: {str(e)}")

    @http.route('/api/whatsapp_users', type='http', auth='public', methods=['GET'], csrf=False)
    def get_whatsapp_users(self):
        """
        Obtiene la lista de usuarios de WhatsApp disponibles.
        
        Returns:
            Response: Respuesta HTTP con la lista de usuarios.
        """
        try:
            self.logger.info("Consultando listado de usuarios de WhatsApp")
            users = self.user_service.get_all_users()
            return self.response_builder.success(data={"users": users})
        except Exception as e:
            self.logger.error("Error obteniendo usuarios de WhatsApp", exc_info=True)
            return self.response_builder.error("Error interno del servidor", status_code=500)