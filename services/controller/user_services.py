from odoo import api, SUPERUSER_ID
from typing import List, Dict, Any
from odoo.http import request
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class UserService:
    """
    Servicio que implementa la lógica de negocio para operaciones
    relacionadas con usuarios de WhatsApp.
    """
    
    def __init__(self):
        self.model_name = 'message_app.message_user'
        self.logger = ExtraLoggerConfig().get_logger("user_services")
    
    def _get_model(self) -> Any:
        """
        Obtiene el modelo de usuarios de WhatsApp con permisos de superusuario.
        
        Returns:
            Model: Instancia del modelo con permisos elevados.
        """
        return request.env[self.model_name].sudo()
    
    def initial_load(self) -> bool:
        """
        Realiza la carga inicial de datos de usuarios desde el sistema externo.
        
        Returns:
            bool: True si la carga fue exitosa.
            
        Raises:
            Exception: Si ocurre algún error durante la carga.
        """
        self.logger.info("Ejecutando carga inicial de usuarios")
        model = self._get_model()
        result = model.initial_load()
        self.logger.info(f"Carga inicial completada: {result}")
        return result
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los usuarios de WhatsApp disponibles.
        
        Returns:
            list: Lista de diccionarios con datos de usuarios.
        """
        model = self._get_model()
        users = model.search([])
        
        return [
            {
                'id': user.id, 
                'name': user.display_name
            } for user in users
        ]
    
    @api.model
    def create_user(self, user_data: Dict[str, Any]) -> int:
        """
        Crea un nuevo usuario de WhatsApp.
        
        Args:
            user_data (dict): Datos del usuario a crear.
            
        Returns:
            int: ID del usuario creado.
        """
        model = self._get_model()
        new_user = model.create(user_data)
        return new_user.id