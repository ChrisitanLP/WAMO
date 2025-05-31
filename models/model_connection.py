from odoo import models, fields, api
from odoo.exceptions import ValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from .mixins.loggable import LoggableMixin
from ..utils.validation.phone_validator import PhoneValidator
from ..utils.validation.color_validator import ColorValidator

class MessageConnection(models.Model, LoggableMixin):
    """
    Model Connection Model that manages Model connections and their relationships.
    Implements clean code principles, SOLID principles, and includes validation and error handling.
    """
    _name = 'message_app.message_connection'
    _description = 'Model Connection'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']
    _order = 'create_date DESC'

    # region Fields
    name = fields.Char(
        string='Connection Name',
        required=True,
        index=True,
        tracking=True,
        help="Unique identifier for the Model connection"
    )

    color = fields.Char(
        string='Color',
        default='#cccccc',
        tracking=True,
        help="Color identifier for the connection"
    )

    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        index=True,
        tracking=True,
        help="Model phone number for this connection"
    )

    active = fields.Boolean(
        default=True,
        tracking=True
    )

    connection_attempts = fields.Integer(
        string='Connection Attempts',
        default=0,
        help="Number of attempts to establish a connection."
    )

    last_connection = fields.Datetime(
        string='Last Connection',
        readonly=True,
        tracking=True
    )

    users = fields.One2many(
        'message_app.message_user',
        'connection_id',
        string='Users',
        copy=False
    )
    
    # endregion

    # region SQL Constraints
    _sql_constraints = [
        ('unique_name', 'unique(name)',
         'Connection name must be unique per company.'),
        ('unique_phone', 'unique(phone_number)',
         'Phone number must be unique per company.')
    ]
    # endregion

    # region Validation Methods
    @api.constrains('phone_number')
    def _check_phone_number(self) -> None:
        """Validates phone number format"""
        for record in self:
            if not PhoneValidator.is_valid_phone(record.phone_number):
                raise ValidationError(f"Invalid phone number: {record.phone_number}")

    @api.constrains('color')
    def _check_color(self) -> None:
        """Validate color format"""
        for record in self:
            if record.color and not ColorValidator.is_valid_color(record.color):
                raise ValidationError(f"Invalid color format: {record.color}")

    def _validate_creation_values(self, vals: Dict[str, Any]) -> None:
        """
        Validate values before creation.
        
        Args:
            vals (dict): Values to validate
        """
        if not vals.get('name'):
            raise ValidationError("Connection name is required")
        
        if not vals.get('phone_number'):
            raise ValidationError("Phone number is required")

        # Normalize color if provided
        if vals.get('color'):
            vals['color'] = ColorValidator.normalize_color(vals['color'])

    def update_connection_status(self, 
                                 connection_id: int, 
                                 is_connected: bool) -> bool:
        """
        Update connection status and tracking information.
        
        Args:
            connection_id (int): ID of the connection
            is_connected (bool): Connection status
        
        Returns:
            bool: True if update was successful
        """
        try:
            connection = self.browse(connection_id)
            if not connection.exists():
                raise ValidationError("Connection does not exist.")

            connection.write({
                'active': is_connected,
                'last_connection': fields.Datetime.now(),
                'connection_attempts': connection.connection_attempts + 1
            })
            return True
        except Exception as e:
            self.logger.exception(f"Error updating connection status: {e}")
            raise ValidationError("Could not update connection status.")
    #endregion

    # region Business Logic Methods
    @api.model
    def get_all_connections(self) -> 'MessageConnection':
        """
        Retrieve all WhatsApp connections with error handling.
        
        Returns:
            recordset: All WhatsApp connections
        """
        try:
            self.logger.debug("Fetching all connections.")
            return self.search([])
        except Exception as e:
            self.logger.exception(f"Error fetching connections: {e}")
            raise ValidationError("Could not retrieve connections.")


    def delete_connection(self, connection_id: int) -> bool:
        """
        Delete a specific WhatsApp connection.
        
        Args:
            connection_id (int): ID of connection to delete
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            connection = self.browse(connection_id)
            if not connection.exists():
                self.logger.warning(f"Tried to delete non-existent connection {connection_id}")
                raise ValidationError("Connection does not exist.")

            self.logger.info(f"Deleting connection {connection_id}")
            connection.unlink()
            return True
        except Exception as e:
            self.logger.exception(f"Error deleting connection {connection_id}: {e}")
            raise ValidationError("Could not delete connection.")

    @api.model_create_multi
    def create(self, vals_list: List[Dict[str, Any]]):
        for vals in vals_list:
            self._validate_creation_values(vals)
        return super().create(vals_list)

    @api.model
    def add_connection(self, 
                       name: str, 
                       phone_number: str, 
                       color: Optional[str] = None) -> 'MessageConnection':
        """
        Add a new WhatsApp connection.
        
        Args:
            name (str): Connection name
            phone_number (str): Phone number
            color (str, optional): Connection color
        
        Returns:
            recordset: Created connection
        """
        try:
            vals = {
                'name': name,
                'phone_number': phone_number,
                'color': color or '#cccccc',
                'last_connection': datetime.now(),
                'connection_attempts': 1
            }
            self._validate_creation_values(vals)
            return self.create(vals)
        except Exception as e:
            self.logger.error(f"Error adding connection: {e}")
            raise ValidationError("Could not add connection. Please try again.")
    # endregion

    def get_inactive_connections(self, 
                                 days: int = 30) -> 'MessageConnection':
        """
        Retrieve connections inactive for a specified number of days.
        
        Args:
            days (int, optional): Number of days of inactivity. Defaults to 30.
        
        Returns:
            recordset: Inactive connections
        """
        cutoff = fields.Datetime.to_string(datetime.now() - timedelta(days=days))
        return self.search([
            ('last_connection', '<=', cutoff),
            ('active', '=', False)
        ])