from ...models.model_contact import MessageContact
from typing import List, Dict, Any, Optional
from odoo.http import request, Response
from ...utils.response.image import ImageHandler
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class ContactService:
    """Service class for handling contact-related operations."""

    def __init__(self):
        self.logger = ExtraLoggerConfig().get_logger("contact_services")

    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts based on name or phone number."""
        try:
            domain = ['|', ('name', 'ilike', query), ('phone_number', 'ilike', query)]
            contacts = request.env['message_app.message_contact'].search(domain)
            
            # Return the list of contacts with all needed properties
            return [{
                'id': contact.id,
                'name': contact.name,
                'serialized': contact.serialized,
                'phone_number': contact.phone_number,
                'profile_pic_url': contact.profile_pic_url,
                'user_display_name': contact.user_id.display_name,
                'user_id': contact.user_id.id,
                'color': contact.user_id.connection_id.color or '#cccccc'
            } for contact in contacts]
        except Exception as e:
            self.logger.error(f"Error buscando contactos: {e}", exc_info=True)
            return [] 

    def save_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new WhatsApp contact."""
        try:
            client_id = data['clientId']
            contact_number = data['contactNumber']
            contact_name = data['contactName']
            serialized_contact = f"{contact_number}@c.us"

            existing_contact = self._check_existing_contact(contact_number, client_id, serialized_contact)
            if existing_contact:
                return {'status': 'exists', 'message': 'El contacto ya existe.'}

            user = self._get_user(client_id)
            if not user:
                return {'status': 'error', 'message': 'Usuario no encontrado.'}

            contact_data = self._prepare_contact_data(user, contact_number, contact_name, serialized_contact)
            new_contact = request.env['message_app.message_contact']._create_or_update_contact(contact_data)

            return {
                'status': 'success',
                'message': 'Contacto añadido exitosamente.',
                'reload': True
            }
        except Exception as e:
            self.logger.error(f"Error guardando contacto: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def add_contact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new contact to the system."""
        try:
            name = data.get('name', '').strip()
            phone_number = data.get('phone_number', '').strip()
            profile_pic_url = data.get('profile_pic_url')

            if not all([name, phone_number]):
                return {'status': 'error', 'message': 'Faltan parámetros requeridos'}

            existing_contact = self._check_existing_partner(phone_number)
            if existing_contact:
                return {'status': 'error', 'message': 'El contacto ya existe'}

            image_data = ImageHandler.download_and_convert_image(profile_pic_url) if profile_pic_url else None
            
            contact = request.env['res.partner'].create({
                'name': name,
                'phone': phone_number,
                'image_1920': image_data,
            })

            return {'status': 'success', 'contact_id': contact.id}
        except Exception as e:
            self.logger.error(f"Error agregando contacto: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _check_existing_partner(self, phone_number: str) -> Optional[Any]:
        """Check if a partner with the given phone number already exists."""
        return request.env['res.partner'].search([('phone', '=', phone_number)], limit=1)


    def _check_existing_contact(self, phone_number: str, client_id: int, serialized: str) -> Optional[Any]:
        """Check if contact already exists."""
        return request.env['message_app.message_contact'].search([
            ('phone_number', '=', phone_number),
            ('user_id', '=', client_id),
            ('serialized', '=', serialized)
        ], limit=1)

    def _get_user(self, client_id: int) -> Optional[Any]:
        """Get user by ID."""
        return request.env['message_app.message_user'].search([('id', '=', client_id)])

    def _prepare_contact_data(self, user: Any, contact_number: str, contact_name: str, serialized_contact: str) -> Dict[str, Any]:
        """Prepare contact data for creation."""
        return {
            'id': serialized_contact,
            'clientNumber': user.phone_number,
            'phone_number': contact_number,
            'name': contact_name,
            'profilePicUrl': 'https://cdn.playbuzz.com/cdn/913253cd-5a02-4bf2-83e1-18ff2cc7340f/c56157d5-5d8e-4826-89f9-361412275c35.jpg'
        }