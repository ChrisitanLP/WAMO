from typing import Optional, List, Dict, Any, Union
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from .mixins.loggable import LoggableMixin
from ..utils.constants import DEFAULT_PROFILE_PIC_URL, CHAT_STATUSES
from ..services.model.chat_services import ChatService
from ..utils.validation.serialized_validator import SerializedValidator
from ..utils.validation.phone_validator import PhoneValidator

class MessageChat(models.Model, LoggableMixin):
    _name = 'message_app.message_chat'
    _description = 'Model Chat'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']

    # region Fields
    # Basic Fields
    serialized = fields.Char(
        string='Serialized', 
        required=True, 
        index=True
    )
    phone_number = fields.Char(
        string='Phone Number', 
        required=True, 
        index=True,
        tracking=True
    )
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True
    )
    timestamp = fields.Datetime(
        string='Timestamp', 
        default=fields.Datetime.now
    )
    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True
    )

    # Chat Status Fields
    is_group = fields.Boolean(
        string='Is Group', 
        default=False
    )
    unread_count = fields.Integer(
        string='Unread Count', 
        default=0
    )
    archived = fields.Boolean(
        string='Archived', 
        default=False
    )
    pinned = fields.Boolean(
        string='Pinned', 
        default=False
    )
    status = fields.Selection(
        CHAT_STATUSES,
        string='Estado',
        default='pendiente'
    )

    # Content Fields
    profile_pic_url = fields.Text(
        string='Profile Picture URL', 
        default=DEFAULT_PROFILE_PIC_URL
    )
    last_message_body = fields.Text(
        string='Last Message Body'
    )
    last_message_type = fields.Char(
        string='Last Message Type'
    )

    # Relationships
    group_id = fields.Many2one('message_app.message_group', 
                              string='Group', 
                              ondelete='cascade'
    )
    user_id = fields.Many2one('message_app.message_user', 
                             string='User Account', 
                             ondelete='cascade',
                             required=True
    )
    messages = fields.One2many('message_app.message_message', 
                             'chat_id', 
                             string='Messages'
    )
    user_attending_id = fields.Many2one('res.users', 
                                      string='Atendido por', 
                                      ondelete='set null'
    )
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
            parsed_number = PhoneValidator.parse(record.phone_number, None)
            if not PhoneValidator.is_valid_number(parsed_number):
                raise ValidationError(f"Invalid phone number: {record.phone_number}")
    # endregion

    @api.constrains('is_group', 'group_id')
    def _check_group_id(self) -> None:
        """Validates group-related constraints."""
        for record in self:
            if record.is_group and not record.group_id:
                raise ValidationError("Group chats must have a group_id.")
            if not record.is_group and record.group_id:
                raise ValidationError("Non-group chats cannot have a group_id.")

    @api.model
    def sync_chats(self, initial_sync: bool = False) -> None:
        """Synchronizes chats from the API."""
        try:
            if initial_sync:
                self._perform_initial_sync()
            else:
                self._perform_incremental_sync()
        except Exception as e:
            self.logger.error(f"Chat sync failed: {e}")
            raise UserError("Error synchronizing chats.")

    def _perform_initial_sync(self) -> None:
        """Performs initial synchronization of chats."""
        chat_service = ChatService(self.env)
        chats_data = chat_service.get_unread_chats()
        
        # Validar la respuesta de la API
        if not chats_data:
            self.logger.error("No chats received from API.")
            raise UserError("Failed to load chats from API.")
        
        # Extraer la lista de chats del diccionario si es necesario
        chats = self._extract_chats_from_response(chats_data)
        
        if chats:
            self._batch_process_chats(chats)
            self._update_sync_date()
        else:
            self.logger.info("No chats to process after data extraction.")

    def _perform_incremental_sync(self) -> None:
        """Performs incremental synchronization of chats."""
        last_sync = self.env['ir.config_parameter'].sudo().get_param('last_sync_date')
        if not last_sync:
            return self._perform_initial_sync()
        
        chat_service = ChatService(self.env)
        chats_data = chat_service.get_unread_chats(last_sync=last_sync)
        
        # Extraer la lista de chats del diccionario si es necesario
        chats = self._extract_chats_from_response(chats_data)
        
        if chats:
            self._batch_process_chats(chats)
            self._update_sync_date()
    
    def _extract_chats_from_response(self, response_data: Union[Dict, List]) -> List:
        """
        Extracts chats list from API response which might be a dict or list.
        
        Args:
            response_data: Data from API which could be a dict or list
            
        Returns:
            List of chat data
        """
        if isinstance(response_data, list):
            return response_data
            
        if isinstance(response_data, dict):
            # Si la respuesta es un diccionario, buscar claves comunes que contengan la lista de chats
            for key in ['chats', 'data', 'results', 'items']:
                if key in response_data and isinstance(response_data[key], list):
                    self.logger.info(f"Extracted chats from '{key}' key in response")
                    return response_data[key]
                    
            # Si no encontramos una clave específica pero hay una lista en algún valor
            for key, value in response_data.items():
                if isinstance(value, list) and len(value) > 0:
                    # Verificar si el primer elemento parece un chat (contiene campos típicos)
                    first_item = value[0]
                    if isinstance(first_item, dict) and any(k in first_item for k in ['id', 'name', 'phone_number']):
                        self.logger.info(f"Found chat list in '{key}' key")
                        return value
                        
            # Si no hay una lista clara de chats pero el diccionario contiene campos de chat,
            # podría ser un solo chat, lo devolvemos como lista
            if any(k in response_data for k in ['id', 'name', 'phone_number']):
                self.logger.info("Response appears to be a single chat, converting to list")
                return [response_data]
                
            self.logger.warning(f"Could not extract chats from dictionary response: {list(response_data.keys())}")
            return []
            
        # Si no es ni lista ni diccionario
        self.logger.error(f"Unexpected response data type: {type(response_data)}")
        return []

    def _batch_process_chats(self, chats: List[Dict], batch_size: int = 100) -> None:
        """Processes chats in batches for better performance."""
        if not chats:
            self.logger.warning("No chats to process in batch")
            return
            
        if not isinstance(chats, list):
            self.logger.error(f"Unexpected data type for chats: {type(chats)}")
            return
            
        for i in range(0, len(chats), batch_size):
            batch = chats[i:i + batch_size]
            self._process_chat_batch(batch)

    def _process_chat_batch(self, chats: List[Dict]) -> None:
        """Processes a batch of chats."""
        for chat_data in chats:
            try:
                if not isinstance(chat_data, dict):
                    self.logger.warning(f"Skipping invalid chat data (not a dict): {type(chat_data)}")
                    continue
                    
                self._create_or_update_chat(chat_data)
            except Exception as e:
                chat_id = chat_data.get('id', {})
                serialized = chat_id.get('_serialized', 'unknown') if isinstance(chat_id, dict) else 'unknown'
                self.logger.warning(f"Error processing chat {serialized}: {e}")

    def _create_or_update_chat(self, chat_data: Dict) -> None:
        """Creates or updates a chat record."""
        values = self._prepare_chat_values(chat_data)
        if not values:
            return

        chat = self._find_existing_chat(values['serialized'], values['user_id'])
        if chat:
            if chat.status == 'atendido':
                values['status'] = 'pendiente'
            chat.write(values)
        else:
            self.create(values)

    def _prepare_chat_values(self, chat_data: Dict) -> Optional[Dict]:
        """Prepares chat values for creation/update."""
        try:
            # Extraer los campos necesarios con manejo seguro
            chat_id = chat_data.get('id', {})
            if not isinstance(chat_id, dict):
                self.logger.warning(f"Invalid chat_id structure: {chat_id}")
                return None
                
            serialized_id = chat_id.get('_serialized')
            user_id = chat_id.get('user')
            
            # Obtener el número de teléfono del cliente
            phone_number = chat_data.get('client')
            if not phone_number:
                phone_number = user_id  # Fallback al user_id si client no está presente
            
            if not serialized_id or not user_id:
                self.logger.warning(f"Missing essential chat data fields: {chat_data}")
                return None

            user = self._find_user(phone_number)
            if not user:
                self.logger.warning(f"No matching user found for phone: {phone_number}")
                return None

            timestamp = self._parse_timestamp(chat_data.get('timestamp'))
            group_id = self._handle_group_data(chat_data) if self._is_group_chat(chat_data) else False

            # Manejo seguro para estructuras anidadas
            last_message = chat_data.get('lastMessage', {})
            if not isinstance(last_message, dict):
                last_message = {}
                
            return {
                'serialized': serialized_id,
                'phone_number': user_id,
                'name': chat_data.get('name', 'Unknown'),
                'timestamp': timestamp,
                'is_group': self._is_group_chat(chat_data),
                'unread_count': chat_data.get('unreadCount', 0),
                'archived': chat_data.get('archived', False),
                'pinned': chat_data.get('pinned', False),
                'last_message_body': last_message.get('body', ''),
                'last_message_type': last_message.get('type', ''),
                'group_id': group_id,
                'user_id': user.id,
                'profile_pic_url': chat_data.get('profilePicUrl', DEFAULT_PROFILE_PIC_URL),
                'last_sync_date': fields.Datetime.now()
            }
        except KeyError as e:
            self.logger.error(f"Missing required field in chat data: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error preparing chat values: {e}", exc_info=True)
            return None

    def _find_existing_chat(self, serialized: str, user_id: int) -> Optional["MessageChat"]:
        """Finds an existing chat by serialized ID and user ID."""
        return self.search([
            ('serialized', '=', serialized),
            ('user_id', '=', user_id)
        ], limit=1)

    def _find_user(self, phone_number: str) -> Optional[models.Model]:
        """Finds a user by phone number."""
        return self.env['message_app.message_user'].search([
            ('phone_number', '=', phone_number)
        ], limit=1)

    def _is_group_chat(self, chat_data: Dict[str, Any]) -> bool:
        """Determines if the chat is a group chat."""
        is_group = chat_data.get('isGroup')
        if is_group is None:
            # Verificar en la estructura serializada
            serialized = chat_data.get('id', {}).get('_serialized', '')
            return '@g.us' in serialized if serialized else False
        return is_group

    def _handle_group_data(self, chat_data: Dict[str, Any]) -> Optional[int]:
        """Handles group-related data and returns group_id if applicable."""
        if 'groupMetadata' not in chat_data:
            return False
            
        group_data = chat_data['groupMetadata']
        group_id = self.env['message_app.message_group'].create_or_update_group(group_data)
        
        if isinstance(group_id, int):
            group = self.env['message_app.message_group'].browse(group_id)
            return group.id if group else False
        return False

    def _parse_timestamp(self, timestamp: Optional[int]) -> datetime:
        """Parses timestamp from chat data."""
        if timestamp:
            try:
                return datetime.utcfromtimestamp(timestamp)
            except (TypeError, ValueError) as e:
                self.logger.warning(f"Invalid timestamp format: {timestamp} - {e}")
        return datetime(2024, 1, 1)

    def _load_chats_async(self, start_page: int):
        """Carga chats adicionales de manera asincrónica."""
        try:
            chat_service = ChatService(self.env)
            chats_data = chat_service.get_unread_chats(page=start_page)
            
            # Si no hay datos o es un diccionario vacío, termina sin error
            if not chats_data:
                self.logger.info(f"No chats found on page {start_page}")
                return
            
            # Extraer la lista de chats del diccionario si es necesario
            chats = self._extract_chats_from_response(chats_data)
            
            if chats:
                self._batch_process_chats(chats)
                self.logger.info(f"Successfully processed {len(chats)} chats from page {start_page}")
            else:
                self.logger.info(f"No chats to process on page {start_page}")
        except Exception as e:
            # Log the error but don't crash the cron job
            self.logger.error(f"Error in async chat loading for page {start_page}: {e}", exc_info=True)

    def _update_sync_date(self) -> None:
        """Updates the last synchronization date."""
        last_sync_date = fields.Datetime.now()
        self.env['ir.config_parameter'].sudo().set_param('last_sync_date', last_sync_date)