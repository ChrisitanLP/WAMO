# utils/validators.py
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    message: str = ""
    error_message: str = None

class PayloadValidator:
    """Validator for API payloads."""

    def validate_contact_payload(self, payload):
        """Validate contact payload."""
        required_fields = ['clientId', 'contactNumber', 'contactName']
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            return ValidationResult(False, f"Missing required fields: {', '.join(missing_fields)}")
        return ValidationResult(True)

    def validate_new_contact_payload(self, payload):
        """Validate new contact payload."""
        name = payload.get('name', '').strip()
        phone_number = payload.get('phone_number', '').strip()
        
        if not name or not phone_number:
            return ValidationResult(False, "Name and phone number are required")
        return ValidationResult(True)

    def validate_payload(self, payload, required_fields):
        """
        Valida un payload JSON y asegura que todos los campos requeridos estén presentes.
        
        Args:
            payload (dict): Payload JSON a validar
            required_fields (list): Lista de campos requeridos
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not payload:
            return False, "Payload vacío"
            
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return False, f"Campos requeridos faltantes: {', '.join(missing_fields)}"
        
        return True, None

    def validate_json_payload(self, payload, required_fields):
        """
        Validate JSON payload and ensure all required fields are present.
        
        Args:
            payload (dict): JSON payload to validate
            required_fields (list): List of required field names
            
        Returns:
            ValidationResult: Result of validation with validity status and error message
        """
        if not payload:
            return ValidationResult(False, "No se proporcionaron datos en la solicitud.")
            
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            return ValidationResult(
                False, 
                f"Faltan campos requeridos: {', '.join(missing_fields)}"
            )
            
        return ValidationResult(True)