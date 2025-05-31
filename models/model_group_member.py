from odoo import models, fields, api
import phonenumbers
from odoo.exceptions import UserError, ValidationError
from typing import Dict, List, Optional
from .mixins.loggable import LoggableMixin
from ..utils.validation.phone_validator import PhoneValidator
from ..utils.validation.serialized_validator import SerializedValidator

class MessageGroupMember(models.Model, LoggableMixin):
    _name = 'message_app.message_group_member'
    _description = 'Model Group Member'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']
    
    # region Fields
    serialized = fields.Char(
        string='Serialized ID',
        required=True,
        index=True,
        help="Unique identifier for the member"
    )
    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        index=True,
        help="Member's phone number"
    )
    is_admin = fields.Boolean(
        default=False,
        help="Indicates if the member is a group admin"
    )
    join_date = fields.Datetime(
        default=fields.Datetime.now,
        help="Date when the member joined the group"
    )
    
    # Relationships
    group_id = fields.Many2one(
        'message_app.message_group',
        string='Group',
        required=True,
        ondelete='cascade',
        index=True
    )
    # endregion
    
    # Constraints
    _sql_constraints = [
        ('unique_group_user', 'unique(group_id, phone_number)',
         'A user can only be a member of the same group once.')
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

    # CRUD Methods
    @api.model
    def create_or_update_members(self, group_id: int, participants: List[Dict]) -> None:
        """
        Creates or updates group members in the database.
        
        Args:
            group_id (int): ID of the WhatsApp group
            participants (list): List of participant data
            
        Raises:
            ValidationError: If input data is invalid
        """
        self._validate_participants_data(participants)
        
        try:
            with self.env.cr.savepoint():
                self._process_member_updates(group_id, participants)
                self._remove_old_members(group_id, participants)
                
        except Exception as e:
            self.logger.error("Error in create_or_update_members: %s", str(e), exc_info=True)
            raise UserError(f"Failed to update group members: {str(e)}")

    # Helper Methods
    def _validate_participants_data(self, participants: List[Dict]) -> None:
        """
        Validates the participant data structure.
        
        Args:
            participants (list): Data to validate
            
        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(participants, list):
            raise ValidationError("Participants data must be a list")
            
        for participant in participants:
            if not isinstance(participant, dict):
                raise ValidationError("Each participant must be a dictionary")
            if 'id' not in participant:
                raise ValidationError("Missing required field: id in participant data")

    def _process_member_updates(self, group_id: int, participants: List[Dict]) -> None:
        """
        Processes member updates by creating new members and updating existing ones.
        
        Args:
            group_id (int): ID of the WhatsApp group
            participants (list): List of participant data
        """
        existing_members = self._get_existing_members(group_id)
        existing_serialized = {member.serialized: member for member in existing_members}
        
        for participant in participants:
            member_data = self._prepare_member_data(participant, group_id)
            if not member_data:
                continue
                
            if member_data['serialized'] in existing_serialized:
                existing_serialized[member_data['serialized']].write(member_data)
            else:
                self.create(member_data)

    def _get_existing_members(self, group_id: int) -> 'MessageGroupMember':
        """
        Retrieves existing members for a group.
        
        Args:
            group_id (int): ID of the WhatsApp group
            
        Returns:
            RecordSet: Existing member records
        """
        return self.search([('group_id', '=', group_id)])

    def _prepare_member_data(self, participant: Dict, group_id: int) -> Optional[Dict]:
        """
        Prepares member data for database operations.
        
        Args:
            participant (dict): Participant information
            group_id (int): ID of the WhatsApp group
            
        Returns:
            dict: Prepared member data or None if invalid
        """
        serialized = participant['id'].get('_serialized')
        phone_number = participant['id'].get('user')
        
        if not serialized or not phone_number:
            return None
            
        return {
            'serialized': serialized,
            'phone_number': phone_number,
            'group_id': group_id,
            'is_admin': participant.get('isAdmin', False)
        }

    def _remove_old_members(self, group_id: int, participants: List[Dict]) -> None:
        """
        Removes members that are no longer in the group.
        
        Args:
            group_id (int): ID of the WhatsApp group
            participants (list): List of current participants
        """
        current_serialized = {p['id']['_serialized'] for p in participants if '_serialized' in p['id']}
        existing_members = self._get_existing_members(group_id)
        
        members_to_remove = existing_members.filtered(
            lambda m: m.serialized not in current_serialized
        )
        
        if members_to_remove:
            members_to_remove.unlink()