from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from typing import Optional, List, Dict, Union
import phonenumbers
from .mixins.loggable import LoggableMixin
from ..utils.constants import DEFAULT_PROFILE_PIC_URL
from ..services.model.contact_services import ContactService
from ..utils.validation.phone_validator import PhoneValidator
from ..utils.validation.serialized_validator import SerializedValidator

class MessageContact(models.Model, LoggableMixin):
    _name = 'message_app.message_contact'
    _description = 'Model Contact'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']

    # region Fields
    serialized = fields.Char(
        string='Serialized', 
        required=True, 
        index=True
    )
    phone_number = fields.Char(
        string='Phone Number', 
        required=True,
        index=True
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    profile_pic_url = fields.Text(
        string='Profile Pic URL', 
        default=DEFAULT_PROFILE_PIC_URL
    )
    user_id = fields.Many2one('message_app.message_user', 
                             string='User Account', 
                             ondelete='cascade', 
                             required=True)
    # endregion

    _sql_constraints = [
        ('unique_serialized', 
        'unique(serialized, user_id)', 
         'The serialized value combined with user ID must be unique.')
    ]

    # region Validations
    @api.constrains('serialized')
    def _check_serialized_validity(self):
        for record in self:
            if not SerializedValidator.is_valid_serialized(record.serialized):
                raise UserError("Invalid serialized format. It must be a valid phone number followed by @c.us.")

    # Validation Methods
    @api.constrains('phone_number')
    def _check_phone_number(self):
        """Validates phone number format"""
        for record in self:
            try:
                parsed_number = PhoneValidator.parse(record.phone_number, None)
                if not PhoneValidator.is_valid_number(parsed_number):
                    raise ValidationError(f"Invalid phone number: {record.phone_number}")
            except phonenumbers.NumberParseException:
                raise ValidationError(f"Could not parse phone number: {record.phone_number}")
    # endregion

    @api.model
    def sync_contacts(self, initial_sync: bool = False) -> None:
        """Synchronizes contacts from the API, either initial or incremental."""
        try:
            if initial_sync:
                self._perform_initial_sync()
            else:
                self._perform_incremental_sync()
        except Exception as e:
            self.logger.error(f"Contact sync failed: {e}")
            raise UserError("Error synchronizing contacts.")

    def _perform_initial_sync(self) -> None:
        """Performs initial synchronization of contacts."""
        contacts = self._fetch_contacts()
        if not contacts:
            self.logger.error("No contacts received from API during initial sync.")
            raise UserError("Failed to load contacts from API.")
        
        self._batch_process_contacts(contacts)

    def _perform_incremental_sync(self) -> None:
        """Performs incremental synchronization of contacts."""
        last_sync_raw = self.env['ir.config_parameter'].sudo().get_param('last_sync_date')
        last_sync: Optional[str] = str(last_sync_raw) if isinstance(last_sync_raw, str) else None
        
        if not last_sync:
            return self._perform_initial_sync()

        contacts = self._fetch_contacts(last_sync=last_sync)
        if contacts:
            self._batch_process_contacts(contacts)

    def _fetch_contacts(self, page: int = 1, last_sync: Optional[str] = None) -> List[Dict]:
        """Fetches contacts from the API with pagination support."""
        try:
            all_contacts = []
            current_page = page
            has_more_pages = True
            
            while has_more_pages:
                params: Dict[str, Union[int, str]] = {'page': current_page}
                if last_sync:
                    params['last_sync'] = last_sync

                contact_service = ContactService()
                response = contact_service.get_contacts(params)
                
                # Validar formato de respuesta
                if isinstance(response, dict):
                    # Si recibimos un diccionario con estructura de paginación
                    contacts = response.get('contacts', [])
                    total_pages = response.get('totalPages', 1)
                    current_page_num = response.get('currentPage', current_page)
                    
                    has_more_pages = current_page_num < total_pages
                    current_page += 1
                elif isinstance(response, list):
                    # Si recibimos directamente una lista de contactos
                    contacts = response
                    has_more_pages = len(contacts) > 0  # Asumimos que hay más páginas si recibimos datos
                    current_page += 1
                else:
                    self.logger.error(f"Invalid contact data format: expected list or dict, got {type(response)}")
                    raise UserError("Invalid data format received from API")
                
                # Si no hay más contactos, terminamos el bucle
                if not contacts:
                    has_more_pages = False
                    break
                    
                # Añadir contactos a la lista completa
                all_contacts.extend(contacts)
                
                # Registrar progreso
                self.logger.info(f"Fetched {len(contacts)} contacts from page {current_page-1}")
                
                # Limitar el número de páginas para evitar bucles infinitos (opcional)
                if current_page > 100:  # Límite arbitrario de 100 páginas
                    self.logger.warning("Reached maximum page limit (100). Stopping pagination.")
                    break
                    
            return all_contacts
        except Exception as e:
            self.logger.error(f"Error fetching contacts: {e}")
            raise UserError(f"Failed to fetch contacts from API: {str(e)}")

    def _batch_process_contacts(self, contacts: List[Dict], batch_size: int = 100) -> None:
        """Processes contacts in batches for better performance."""
        if not contacts:
            self.logger.info("No contacts to process")
            return
            
        if not isinstance(contacts, list):
            self.logger.error(f"Invalid contacts data type: {type(contacts)}")
            raise UserError("Expected list of contacts but received different data type")
            
        try:
            for i in range(0, len(contacts), batch_size):
                batch = contacts[i:i + batch_size]
                if batch:
                    self._process_contact_batch(batch)
        except TypeError as e:
            self.logger.error(f"Type error in batch processing: {e}", exc_info=True)
            raise UserError(f"Type error processing contacts: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error in batch processing: {e}", exc_info=True)
            raise UserError(f"Error processing contacts: {str(e)}")

    def _process_contact_batch(self, contacts: List[Dict]) -> None:
        """Processes a batch of contacts."""
        for contact_data in contacts:
            try:
                if not isinstance(contact_data, dict):
                    self.logger.warning(f"Skipping invalid contact data type: {type(contact_data)}")
                    continue
                    
                self._create_or_update_contact(contact_data)
            except Exception as e:
                self.logger.warning(f"Error processing contact {contact_data.get('id', 'unknown')}: {e}")

    def _create_or_update_contact(self, contact_data: Dict) -> None:
        """Creates or updates a contact and its associated chat."""
        values = self._prepare_contact_values(contact_data)
        if not values:
            return

        contact = self._find_existing_contact(values['serialized'], values['user_id'])
        if contact:
            contact.write(values)
        else:
            contact = self.create(values)

        self._create_or_update_chat(contact, contact_data)

    def _prepare_contact_values(self, contact_data: Dict) -> Optional[Dict]:
        """Prepares contact values for creation/update."""
        if not isinstance(contact_data, dict):
            self.logger.warning(f"Invalid contact data type: {type(contact_data)}")
            return None
            
        serialized_id = contact_data.get('id')
        client_number = contact_data.get('clientNumber')
        
        if not serialized_id:
            self.logger.warning(f"Missing 'id' in contact data: {contact_data}")
            return None
            
        if not client_number:
            self.logger.warning(f"Missing 'clientNumber' in contact data: {contact_data}")
            return None

        user = self._find_user(client_number)
        if not user:
            self.logger.warning(f"No user found for client number: {client_number}")
            return None

        # Extract phone number from serialized ID if not provided
        phone_number = contact_data.get('phone_number', '')
        if not phone_number and '@' in serialized_id:
            # Extract phone number from serialized ID (typically formatted as "number@c.us")
            phone_number = serialized_id.split('@')[0]

        return {
            'serialized': serialized_id,
            'phone_number': phone_number,
            'name': contact_data.get('name', ''),
            'profile_pic_url': contact_data.get('profilePicUrl', DEFAULT_PROFILE_PIC_URL),
            'user_id': user.id
        }

    def _find_existing_contact(self,  serialized: str, user_id: int) -> Optional['MessageContact']:
        """Finds an existing contact by serialized ID and user ID."""
        return self.search([
            ('serialized', '=', serialized),
            ('user_id', '=', user_id)
        ], limit=1)

    def _find_user(self, phone_number: str) -> Optional[models.Model]:
        """Finds a user by phone number."""
        return self.env['message_app.message_user'].search([
            ('phone_number', '=', phone_number)
        ], limit=1)

    def _create_or_update_chat(self, contact: 'MessageContact', contact_data: Dict) -> None:
        """Creates or updates an associated chat for the contact."""
        chat_model = self.env['message_app.message_chat']
        chat_values = self._prepare_chat_values(contact, contact_data)
        
        existing_chat = chat_model.search([
            ('serialized', '=', contact.serialized),
            ('user_id', '=', contact.user_id.id)
        ], limit=1)

        if existing_chat:
            existing_chat.write(chat_values)
        else:
            chat_model.create(chat_values)

    def _prepare_chat_values(self, contact: 'MessageContact', contact_data: Dict) -> Dict:
        """Prepares chat values for creation/update."""
        return {
            'serialized': contact.serialized,
            'phone_number': contact.phone_number,
            'name': contact.name,
            'timestamp': fields.Datetime.now(),
            'is_group': False,
            'unread_count': 0,
            'archived': False,
            'pinned': False,
            'last_message_body': '',
            'last_message_type': '',
            'user_id': contact.user_id.id,
            'profile_pic_url': contact.profile_pic_url
        }