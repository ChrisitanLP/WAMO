# models/sticker_validator.py
import os
from odoo.exceptions import UserError

class StickerValidator:
    """
    Clase para validación de datos de stickers.
    Implementa el patrón Strategy para la validación.
    """
    
    ALLOWED_MIME_TYPES = ['image/webp', 'image/png', 'image/jpeg']
    MAX_FILE_SIZE = 100 * 1024  # 100KB
    
    def validate_sticker_data(self, name, file_path, file_name, mime_type):
        """
        Valida todos los datos del sticker.
        
        Args:
            name (str): Nombre del sticker
            file_path (str): Ruta del archivo
            file_name (str): Nombre del archivo
            mime_type (str): Tipo MIME del archivo
            
        Raises:
            UserError: Si alguna validación falla
        """
        self._validate_name(name)
        self._validate_file_path(file_path)
        self._validate_file_name(file_name)
        self._validate_mime_type(mime_type)
        self._validate_file_size(file_path)
        
    def _validate_name(self, name):
        """Valida el nombre del sticker."""
        if not name or len(name) < 3:
            raise UserError("Sticker name must be at least 3 characters long.")
            
    def _validate_file_path(self, file_path):
        """Valida la ruta del archivo."""
        if not os.path.exists(file_path):
            raise UserError("File does not exist.")
            
    def _validate_file_name(self, file_name):
        """Valida el nombre del archivo."""
        if not file_name.lower().endswith(('.webp', '.png', '.jpg', '.jpeg')):
            raise UserError("Invalid file extension.")
            
    def _validate_mime_type(self, mime_type):
        """Valida el tipo MIME del archivo."""
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise UserError(f"Invalid MIME type. Allowed types: {', '.join(self.ALLOWED_MIME_TYPES)}")
            
    def _validate_file_size(self, file_path):
        """Valida el tamaño del archivo."""
        if os.path.getsize(file_path) > self.MAX_FILE_SIZE:
            raise UserError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE/1024}KB")