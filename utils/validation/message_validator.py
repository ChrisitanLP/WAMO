from odoo.exceptions import ValidationError
from ...models.mixins.message_type import MessageType
import re

class MessageValidator:
    @staticmethod
    def validate_message_data(vals):
        """Validar datos del mensaje según su tipo"""
        if 'type' in vals:
            message_type = vals['type']
            
            if message_type == MessageType.TEXT.value:
                MessageValidator._validate_text(vals)
            elif message_type == MessageType.LOCATION.value:
                MessageValidator._validate_location(vals)
            elif message_type == MessageType.WEB_PAGE.value:
                MessageValidator._validate_web_url(vals)
            elif message_type in [MessageType.IMAGE.value, MessageType.DOCUMENT.value]:
                MessageValidator._validate_file(vals)

    @staticmethod
    def _validate_text(vals):
        if 'text' in vals and not vals['text']:
            raise ValidationError('Text message cannot be empty')

    @staticmethod
    def _validate_location(vals):
        if 'location_latitude' in vals:
            if not -90 <= vals['location_latitude'] <= 90:
                raise ValidationError('Invalid latitude value')
        if 'location_longitude' in vals:
            if not -180 <= vals['location_longitude'] <= 180:
                raise ValidationError('Invalid longitude value')

    @staticmethod
    def _validate_web_url(vals):
        if 'web_url' in vals and vals['web_url']:
            url_pattern = re.compile(
                r'^https?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            if not url_pattern.match(vals['web_url']):
                raise ValidationError('Invalid URL format')

    @staticmethod
    def _validate_file(vals):
        if 'file_name' in vals and not vals['file_name']:
            raise ValidationError('File name is required')