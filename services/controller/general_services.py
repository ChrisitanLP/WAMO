from odoo.http import request
from typing import List, Dict, Any
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class GeneralService:
    """Servicio para gestionar operaciones relacionadas con WhatsApp."""

    def __init__(self):
        self.logger = ExtraLoggerConfig().get_logger("general_services")

    def load_initial_data(self) -> bool:
        """
        Carga todos los datos iniciales necesarios para la operación del sistema.
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            self._load_default_messages()
            self._load_stickers()
            self._load_users()
            self._load_chats()
            self._load_contacts()
            
            return True
        except Exception as e:
            self.logger.error(f"Error al cargar datos iniciales: {e}")
            raise e
    
    def _load_users(self) -> None:
        """Carga inicial de usuarios de WhatsApp."""
        whatsapp_user_model = request.env['message_app.message_user']
        whatsapp_user_model.initial_load()
        self.logger.info('Carga inicial de Usuarios completada.')
        
    def _load_chats(self) -> None:
        """Carga inicial de chats de WhatsApp."""
        whatsapp_chat_model = request.env['message_app.message_chat']
        whatsapp_chat_model.sync_chats()
        self.logger.info('Carga inicial de CHATS completada.')
        
    def _load_contacts(self) -> None:
        """Carga inicial de contactos de WhatsApp."""
        whatsapp_contact_model = request.env['message_app.message_contact']
        whatsapp_contact_model.sync_contacts()
        self.logger.info('Carga inicial de Contactos completada.')
        
    def _load_default_messages(self) -> None:
        """Carga inicial de mensajes predeterminados."""
        default_message_model = request.env['message_app.message_default_message']
        default_message_model.create_default_messages()
        self.logger.info('Mensajes por defecto generados.')
        
    def _load_stickers(self) -> None:
        """Carga inicial de stickers predeterminados."""
        sticker_model = request.env['message_app.message_sticker']
        sticker_model.create_default_stickers_model()
        self.logger.info('Stickers por defecto creados exitosamente.')
    
    def load_initial_chats(self) -> bool:
        """
        Carga únicamente los chats iniciales.
        
        Returns:
            bool: True si la carga fue exitosa
        """
        whatsapp_chat_model = request.env['message_app.message_chat']
        whatsapp_chat_model.sync_chats()
        self.logger.info('Carga inicial de CHATS completada.')
        return True
    
    def get_user_chats(self, user_id: int) -> Any:
        """
        Obtiene los chats relevantes para un usuario específico.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            recordset: Conjunto de registros de chats
        """
        return request.env['message_app.message_chat'].search(
            [
                '|',
                ('unread_count', '>', 0),
                ('user_attending_id', '=', user_id),
                ('status', '!=', 'atendido')
            ],
            order='timestamp desc'
        )
    
    def get_contacts(self) -> Any:
        """
        Obtiene todos los contactos ordenados por nombre.
        
        Returns:
            recordset: Conjunto de registros de contactos
        """
        return request.env['message_app.message_contact'].search(
            [], 
            order='name asc'
        )
    
    def get_template_data(self, template_name: str) -> Dict[str, Any]:
        """
        Obtiene los datos necesarios para renderizar una plantilla específica.
        
        Args:
            template_name (str): Nombre de la plantilla
            
        Returns:
            dict: Datos para la plantilla o None si no es válida
        """
        template_handlers = {
            'contacts_template': self._get_contacts_data,
            'products_template': self._get_products_data,
            'default_messages_template': self._get_default_messages_data
        }
        
        handler = template_handlers.get(template_name)
        if handler:
            return handler()
        return None
    
    def _get_contacts_data(self) -> Dict[str, Any]:
        """Obtiene datos para la plantilla de contactos."""
        contacts = self.get_contacts()
        return {'contacts': contacts}
    
    def _get_products_data(self) -> Dict[str, Any]:
        """Obtiene datos para la plantilla de productos."""
        products = request.env['product.template'].search([])
        return {'products': products}
    
    def _get_default_messages_data(self) -> Dict[str, Any]:
        """Obtiene datos para la plantilla de mensajes por defecto."""
        messages = request.env['message_app.message_default_message'].search([])
        return {'messages': messages}