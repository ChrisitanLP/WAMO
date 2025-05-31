from datetime import datetime
import logging
from typing import Dict, Any
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class DataValidator:
    """Validate input data and user access."""
    
    def validate_user_access(self, user: Any) -> None:
        """Validate user has required access rights."""
        if not user.has_group('base.group_system'):
            raise ValidationError("Unauthorized access")
            
    def validate_connection_data(self, data) -> None:
        """Validate connection data."""
        if not data.get('phone_number'):
            raise ValidationError("Phone number is required")
            
    def validate_chat_data(self, data) -> None:
        """Validate chat search parameters."""
        if not any([data.get('serialized'), data.get('user_id'), data.get('phone_number')]):
            raise ValidationError("At least one search parameter is required")

    def timestamp_to_datetime(timestamp):
        """
        Convierte un timestamp en segundos a un objeto datetime.
        
        Args:
            timestamp (int): El timestamp en segundos o milisegundos.
            
        Returns:
            datetime: El objeto datetime correspondiente o None si hay error.
        """
        try:
            # Verificar si el timestamp está en milisegundos (13 dígitos)
            if timestamp and len(str(int(timestamp))) > 10:
                timestamp = int(timestamp) / 1000  # Convertir a segundos
                
            return datetime.utcfromtimestamp(timestamp) if timestamp else None
        except Exception as e:
            _logger.error(f"Error al convertir timestamp a datetime: {e}")
            return None