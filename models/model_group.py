from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from typing import Dict, List, Optional
from .mixins.loggable import LoggableMixin
from ..services.model.group_services import GroupService
from ..utils.validation.serialized_validator import SerializedValidator

class MessageGroup(models.Model, LoggableMixin):
    _name = 'message_app.message_group'
    _description = 'Model Group'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']

    # region Fields
    serialized = fields.Char(
        string='Serialized ID', 
        required=True, 
        index=True,
        help="Unique identifier for the WhatsApp group"
    )
    group_number = fields.Char(
        string='Group Number',
        required=True,
        help="WhatsApp group phone number"
    )
    group_name = fields.Char(
        string='Group Name',
        required=True,
        help="Name of the WhatsApp group"
    )
    active = fields.Boolean(
        default=True,
        help="Set to false to archive the group"
    )
    members_count = fields.Integer(
        compute='_compute_members_count',
        store=True,
        help="Number of members in the group"
    )
    
    # Relationships
    members = fields.One2many(
        'message_app.message_group_member',
        'group_id',
        string='Members'
    )
    chats = fields.One2many(
        'message_app.message_chat',
        'group_id',
        string='Group Chats'
    )
    # endregion

    _sql_constraints = [
        ('unique_serialized', 
        'unique(serialized)', 
        'The serialized value must be unique.')
    ]

    # Computed Fields
    @api.depends('members')
    def _compute_members_count(self):
        """Computes the number of active members in the group"""
        for group in self:
            group.members_count = len(group.members)

    # region Validations
    @api.constrains('serialized')
    def _check_serialized_validity(self):
        for record in self:
            if not SerializedValidator.is_valid_serialized(record.serialized):
                raise UserError("Invalid serialized format. It must be a valid phone number followed by @c.us.")

    # Validation Methods
    @api.constrains('group_number')
    def _check_group_number_format(self):
        """Validates the format of the group number"""
        for record in self:
            if not record.group_number or not record.group_number.isdigit():
                raise ValidationError("Group number must contain only digits")
    # endregion

    # CRUD Methods
    @api.model
    def create_or_update_group(self, group_data: Dict) -> int:
        """
        Creates or updates a WhatsApp group record in the database.
        
        Args:
            group_data (dict): Dictionary containing group information
            
        Returns:
            int: ID of the created/updated group
            
        Raises:
            ValidationError: If input data is invalid
        """
        self._validate_group_data(group_data)
        
        try:
            with self.env.cr.savepoint():
                group = self._get_or_create_group(group_data)
                self._update_group_members(group, group_data.get('participants', []))
                return group.id
                
        except Exception as e:
            self.logger.error("Error in create_or_update_group: %s", str(e), exc_info=True)
            raise UserError(f"Failed to process group data: {str(e)}")

    # Helper Methods
    def _validate_group_data(self, group_data: Dict) -> None:
        """
        Validates the input group data structure.
        
        Args:
            group_data (dict): Data to validate
            
        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(group_data, dict):
            raise ValidationError("Group data must be a dictionary")
            
        if not group_data.get('id', {}).get('_serialized'):
            raise ValidationError("Missing required field: serialized ID")
            
        if 'participants' in group_data and not isinstance(group_data['participants'], list):
            raise ValidationError("Participants must be a list")

    def _get_or_create_group(self, group_data: Dict) -> models.Model:
        """
        Retrieves existing group or creates a new one.
        
        Args:
            group_data (dict): Group information
            
        Returns:
            WhatsappGroup: The group record
        """
        serialized_id = group_data['id']['_serialized']
        group = self.search([('serialized', '=', serialized_id)], limit=1)
        
        group_values = {
            'group_number': group_data['id'].get('user', ''),
            'group_name': group_data.get('subject', 'Unnamed Group'),
            'serialized': serialized_id,
        }
        
        if group:
            group.write(group_values)
        else:
            group = self.create(group_values)
            
        return group

    def _update_group_members(self, group: models.Model, participants: List[Dict]) -> None:
        """
        Updates the group members list.
        
        Args:
            group (WhatsappGroup): Group record
            participants (list): List of participant data
        """
        if not participants:
            return
            
        member_model = self.env['message_app.message_group_member']
        member_model.create_or_update_members(group.id, participants)
