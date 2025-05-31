
# models/default_message.py
from odoo import models, fields, api
from odoo.exceptions import UserError
from .mixins.message_type import MessageType
from .mixins.loggable import LoggableMixin
from ..utils.validation.message_validator import MessageValidator

class DefaultMessage(models.Model, LoggableMixin):
    _name = 'message_app.message_default_message'
    _description = 'Model Default Message'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']
    _order = 'create_date DESC'

    # Campos básicos
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        index=True
    )
    type = fields.Selection(
        MessageType.to_list(),
        string='Type',
        required=True,
        tracking=True
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

    # Campos específicos por tipo
    text = fields.Text(
        string='Text',
        tracking=True
    )
    location = fields.Char(
        string='Location',
        tracking=True
    )
    location_latitude = fields.Float(
        string='Latitude',
        digits=(16, 8)
    )
    location_longitude = fields.Float(
        string='Longitude',
        digits=(16, 8)
    )
    file_url = fields.Text(
        string='File URL',
        tracking=True
    )
    file_name = fields.Char(
        string='File Name',
        tracking=True
    )
    web_url = fields.Char(
        string='Web Page URL',
        tracking=True
    )

    # Campos computados
    message_count = fields.Integer(
        string='Message Count',
        compute='_compute_message_count',
        store=True
    )

    @api.depends('message_ids')
    def _compute_message_count(self):
        for record in self:
            record.message_count = len(record.message_ids)

    @api.model
    def create_message(self, vals):
        """Crear un nuevo mensaje con validación"""
        try:
            MessageValidator.validate_message_data(vals)
            return super(DefaultMessage, self).create(vals)
        except Exception as e:
            self.logger.error(f"Error creating message: {str(e)}")
            raise UserError(str(e))

    def write(self, vals):
        """Actualizar mensaje con validación"""
        try:
            MessageValidator.validate_message_data(vals)
            return super(DefaultMessage, self).write(vals)
        except Exception as e:
            self.logger.error(f"Error updating message: {str(e)}")
            raise UserError(str(e))

    @api.model
    def create_default_messages(self):
        """Crear mensajes por defecto si no existen"""
        try:
            if not self.search_count([]):
                default_messages = self._get_default_messages()
                for message in default_messages:
                    self.create_message(message)
                self.logger.info("Default messages created successfully")
        except Exception as e:
            self.logger.error(f"Error creating default messages: {str(e)}")
            raise UserError(str(e))

    @api.model
    def _get_default_messages(self):
        """Obtener lista de mensajes por defecto"""
        return [
            {
                'name': 'Saludo',
                'text': 'Hola!!, ¿Cómo puedo ayudarte el día de hoy?.',
                'type': MessageType.TEXT.value
            },
            {
                'name': 'Localización',
                'location': '1234 Company St, Business City, BC 12345',
                'location_latitude': 37.7749,
                'location_longitude': -122.4194,
                'type': MessageType.LOCATION.value
            },
            {
                'name': 'Pagina Web',
                'web_url': 'https://impaldiesel.com/',
                'type': MessageType.WEB_PAGE.value
            }
        ]

    def delete_message(self):
        """Eliminar mensaje de forma segura"""
        try:
            for record in self:
                record.active = False
            self.logger.info(f"Messages marked as inactive: {self.ids}")
        except Exception as e:
            self.logger.error(f"Error deleting messages: {str(e)}")
            raise UserError(str(e))