from odoo import models, fields, api
from odoo.exceptions import UserError
from typing import List, Dict, Any, Tuple, Optional
from .mixins.loggable import LoggableMixin
from ..utils.constants import MESSAGE_STATUSES, MESSAGE_TYPES
from ..utils.validation.serialized_validator import SerializedValidator
from ..services.model.message_services import MessageService
from ..utils.validation.data_validator import DataValidator

class MessageMessage(models.Model, LoggableMixin):
    _name = 'message_app.message_message'
    _description = 'Model Message'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']
    _order = 'timestamp DESC'

    # region Fields
    # Basic Fields
    serialized = fields.Char(
        string='Serialized', 
        required=True, 
        index=True
    )
    body = fields.Text(
        string='Message Body'
    )
    timestamp = fields.Datetime(
        string='Timestamp', 
        index=True
    )
    status = fields.Selection(
        MESSAGE_STATUSES,
        string='Status',
        default='pending'
    )

    # Sender/Receiver Information
    from_me = fields.Boolean(
        string='From Me', 
        index=True
    )
    from_user = fields.Char(
        string='From User', 
        index=True
    )
    to_user = fields.Char(
        string='To User', 
        index=True
    )

    # Media Fields
    media_type = fields.Char(
        string='Media Type'
    )
    has_media = fields.Boolean(
        string='Has Media', 
        default=False
    )
    media_temp_url = fields.Text(
        string='Media Temp Url'
    )
    media_base64 = fields.Text(
        string='Media Base64'
    )
    mime_type = fields.Char(
        string='MIME Type'
    )

    # Message Flags
    is_forwarded = fields.Boolean(
        string='Is Forwarded', 
        default=False
    )
    is_starred = fields.Boolean(
        string='Is Starred', 
        default=False
    )

    # Quoted Message Fields
    has_quoted_msg = fields.Boolean(
        string='Has Quoted Message', 
        default=False
    )
    quoted_serialized = fields.Char('Quoted Serialized')
    quoted_from_user = fields.Char('Quoted From')
    quoted_to_user = fields.Char('Quoted To')
    quoted_body = fields.Text('Quoted Body')
    quoted_type = fields.Char('Quoted Type')
    quoted_timestamp = fields.Datetime('Quoted Timestamp')

    # Location Fields
    location_latitude = fields.Char('Location latitude')
    location_longitude = fields.Char('Location longitude')

    # Relations
    chat_id = fields.Many2one('message_app.message_chat', 
                             string='Chat', 
                             ondelete='cascade',
                             required=True,
                             index=True)
    # endregion

    _sql_constraints = [
        ('unique_serialized', 
        'unique(serialized)', 
        'The serialized value must be unique.')
    ]

    # region Validation
    @api.constrains('serialized')
    def _check_serialized_validity(self):
        for record in self:
            if not SerializedValidator.is_valid_serialized_message(record.serialized):
                raise UserError("Invalid serialized format. It must be a valid phone number followed by @c.us.")
    # endregion

    @api.model
    def initial_load(self, chat_id: int) -> bool:
        """Carga inicial de todos los mensajes de un chat específico"""
        try:
            chat = self.env['message_app.message_chat'].browse(chat_id)
            if not chat:
                raise UserError(f"Chat con ID: {chat_id} no existe.")
            
            if len(chat) != 1:
                raise UserError(f"Se esperaban 1 chat, pero se encontraron {len(chat)}.")
            
            message_service = MessageService(self.env)
            messages: List[Dict[str, Any]] = message_service.get_chat_messages(chat)
            
            if not messages:
                self.logger.warning(f"No se recibieron mensajes para el chat {chat.display_name}.")
                return False
            
            return self._process_messages_batch(chat, messages)
        except Exception as e:
            self.logger.error(f"Error en la carga inicial de mensajes para el chat ID {chat_id}: {e}")
            raise UserError(f"Error en la carga inicial de mensajes: {e}")

    def _get_chat(self, chat_id: int) -> Any:
        """Retrieves and validates chat record."""
        chat = self.env['message_app.message_chat'].browse(chat_id)
        if not chat:
            raise UserError(f"Chat with ID {chat_id} does not exist.")
        if len(chat) != 1:
            raise UserError(f"Expected 1 chat, found {len(chat)}.")
        return chat

    @api.model
    def _process_messages_batch(self, chat: Any, messages: List[Dict[str, Any]], batch_size: int = 100) -> bool:
        """Procesa los mensajes en lotes para optimizar rendimiento"""
        total_messages = len(messages)
        processed = 0
        
        for i in range(0, total_messages, batch_size):
            batch = messages[i:i+batch_size]
            message_values_list = []
            
            # Preparar valores para crear en batch
            for message_data in batch:
                message_values = self._prepare_message_values(chat, message_data)
                if message_values:
                    message_values_list.append(message_values)
            
            # Verificar mensajes existentes para actualizar
            serialized_ids = [vals['serialized'] for vals in message_values_list]
            existing_messages = self.search([
                ('serialized', 'in', serialized_ids)
            ])
            existing_dict = {msg.serialized: msg.id for msg in existing_messages}
            
            # Separar mensajes para crear y actualizar
            to_create = []
            to_update = []
            
            for values in message_values_list:
                if values['serialized'] in existing_dict:
                    values['id'] = existing_dict[values['serialized']]
                    to_update.append(values)
                else:
                    to_create.append(values)
            
            # Crear y actualizar en batch
            if to_create:
                self.create(to_create)
            
            if to_update:
                for update_vals in to_update:
                    msg_id = update_vals.pop('id')
                    self.browse(msg_id).write(update_vals)
            
            processed += len(batch)
            self.logger.info(f"Procesados {processed}/{total_messages} mensajes para el chat {chat.display_name}")
        
        return True
    
    @api.model
    def _prepare_message_values(self, chat: Any, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Prepara los valores para crear o actualizar un mensaje"""
        try:
            message_serialized = message_data.get('id')
            if not message_serialized:
                self.logger.warning("Mensaje sin ID serializado, ignorando")
                return None

            # Convertir timestamps
            timestamp = message_data.get('timestamp')
            naive_datetime = DataValidator.timestamp_to_datetime(timestamp) if timestamp else None
            
            quoted_timestamp = message_data.get('quotedMsg', {}).get('timestamp') if message_data.get('quotedMsg') else None
            quoted_naive_datetime = DataValidator.timestamp_to_datetime(quoted_timestamp) if quoted_timestamp else None
            
            return {
                'chat_id': chat.id,
                'serialized': message_serialized,
                'body': message_data.get('body', ''),
                'from_me': message_data.get('fromMe', False),
                'from_user': message_data.get('from', ''),
                'to_user': message_data.get('to', ''),
                'timestamp': naive_datetime,
                'status': 'sent', 
                'media_type': message_data.get('mediaType', ''),
                'has_media': message_data.get('isMedia', False),
                'mime_type': message_data.get('mediaMimeType', ''),
                'media_temp_url': message_data.get('mediaTempUrl', ''),
                'media_base64': message_data.get('mediaBase64', ''),
                'is_forwarded': message_data.get('isForwarded', False),
                'is_starred': message_data.get('isStarred', False),
                'has_quoted_msg': message_data.get('hasQuotedMsg', False),
                'quoted_serialized': message_data.get('quotedStanzaID', ''),
                'quoted_from_user': message_data.get('quotedParticipant', {}).get('_serialized', '') if message_data.get('quotedParticipant') else '',
                'quoted_to_user': message_data.get('quotedMsg', {}).get('to', '') if message_data.get('quotedMsg') else '',
                'quoted_body': message_data.get('quotedMsg', {}).get('body', '') if message_data.get('quotedMsg') else '',
                'quoted_type': message_data.get('quotedMsg', {}).get('type', '') if message_data.get('quotedMsg') else '',
                'quoted_timestamp': quoted_naive_datetime,
                'location_latitude': message_data.get('location', {}).get('latitude', '') if message_data.get('location') else '',
                'location_longitude': message_data.get('location', {}).get('longitude', '') if message_data.get('location') else ''
            }
        except Exception as e:
            self.logger.error(f"Error preparando valores del mensaje: {e}")
            return None