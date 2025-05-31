import re
from .phone_validator import PhoneValidator

"""Clase para validar codigo serialized."""
class SerializedValidator:
    @staticmethod
    def is_valid_serialized(serialized: str) -> bool:
        """
        Valida el formato del codigo serialized.
        Args:
            serialized (str): Codigo a validar
        Returns:
            bool: True si el formato es válido
        """
        pattern = r'^(\d{6,15})@c\.us$'
        match = re.match(pattern, serialized)
        if not match:
            print(f"❌ Formato incorrecto: {serialized}")  # <-- Agregamos log
            return False
        
        phone_number = match.group(1)  # Extrae el número antes de @c.us
        if not PhoneValidator.is_valid_phone(phone_number):
            print(f"❌ Número de teléfono inválido: {phone_number}")  # <-- Log si el número es inválido
            return False

        return True

    @staticmethod
    def is_valid_serialized_message(serialized: str) -> bool:
        """
        Valida el formato del codigo serialized.
        Args:
            serialized (str): Codigo a validar
        Returns:
            bool: True si el formato es válido
        """
        pattern = r'^(true|false)_(\d{6,15})@c\.us_[A-F0-9]+$'
        match = re.match(pattern, serialized)
        
        if not match:
            print(f"❌ Formato incorrecto: {serialized}")
            return False
        
        phone_number = match.group(2)  # Extrae el número antes de @c.us
        if not PhoneValidator.is_valid_phone(phone_number):
            print(f"❌ Número de teléfono inválido: {phone_number}")
            return False
        
        return True