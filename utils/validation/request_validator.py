from odoo.http import request, Response
from odoo.exceptions import ValidationError

class RequestValidator:
    """
    Validador de requests para endpoints de stickers.
    Implementa validaciones de datos de entrada.
    """

    REQUIRED_CREATE_FIELDS = ['name', 'file_name', 'mime_type']
    ALLOWED_MIME_TYPES = ['image/webp', 'image/png', 'image/jpeg']
    
    def validate_create_request(self, request):
        """
        Valida los datos para crear un sticker.
        Args:
            request: Objeto request de Odoo
        Raises:
            ValueError: Si faltan campos o son inválidos
        """
        # Validar campos requeridos
        for field in self.REQUIRED_CREATE_FIELDS:
            if not request.params.get(field):
                raise ValueError(f"Campo requerido faltante: {field}")

        # Validar tipo MIME
        mime_type = request.params.get('mime_type')
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValueError(f"Tipo MIME no permitido. Permitidos: {', '.join(self.ALLOWED_MIME_TYPES)}")

        # Validar archivo
        if not request.httprequest.files.get('file'):
            raise ValueError("No se proporcionó archivo")

    def validate_update_message_request(self, data):
        """Valida los datos para actualizar un mensaje"""
        if 'type' in data:
            self._validate_message_type(data['type'])

    def validate_create_message_request(self, data):
        """Valida los datos para crear un mensaje"""
        required_fields = ['name', 'type']
        self._validate_required_fields(data, required_fields)
        self._validate_message_type(data.get('type'))

    def _validate_required_fields(self, data, required_fields):
        """Valida campos requeridos"""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValidationError(f"Campos requeridos faltantes: {', '.join(missing_fields)}")

    def _validate_message_type(self, message_type):
        """Valida el tipo de mensaje"""
        valid_types = ['text', 'location', 'image', 'document', 'web_page']
        if message_type not in valid_types:
            raise ValidationError(f"Tipo de mensaje inválido. Tipos válidos: {', '.join(valid_types)}")
