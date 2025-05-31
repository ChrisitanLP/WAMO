import re
import phonenumbers
from typing import Optional
from phonenumbers.phonenumberutil import NumberParseException

class NumberParseExceptions(Exception):
    """Excepción personalizada para errores en el parseo de números."""
    pass

class FakePhoneNumber:
    """Clase simulada para almacenar información de un número telefónico."""
    def __init__(self, country_code: int, national_number: str):
        self.country_code = country_code
        self.national_number = national_number

class PhoneValidator:
    """Clase para validar, normalizar y formatear números telefónicos."""

    COUNTRY_CODES = {
        "EC": 593,  # Ecuador
        "US": 1,    # Estados Unidos
        "MX": 52,   # México
        "AR": 54,   # Argentina
        "BR": 55,   # Brasil
        "CL": 56,   # Chile
        "CO": 57,   # Colombia
        "PE": 51,   # Perú
        "VE": 58,   # Venezuela
        "BO": 591,  # Bolivia
        "PY": 595,  # Paraguay
        "UY": 598,  # Uruguay
        "CA": 1,    # Canadá
        "GB": 44,   # Reino Unido
        "FR": 33,   # Francia
        "DE": 49,   # Alemania
        "IT": 39,   # Italia
        "ES": 34,   # España
        "AU": 61,   # Australia
        "JP": 81,   # Japón
        "CN": 86,   # China
        "IN": 91,   # India
        "ZA": 27,   # Sudáfrica
        "RU": 7,    # Rusia
    }

    @staticmethod
    def parse(phone_number: str, region: Optional[str] = None) -> FakePhoneNumber:
        """
        Simula la función phonenumbers.parse().
        """
        if not phone_number.isdigit():
            raise NumberParseExceptions("Número inválido")

        # Extrae el código de país: máximo 3 dígitos (ejemplo: 593)
        found = False
        for country_code in sorted(PhoneValidator.COUNTRY_CODES.values(), key=lambda x: -len(str(x))):
            if phone_number.startswith(str(country_code)):
                national_number = phone_number[len(str(country_code)):]
                if not national_number:  # Si no hay más dígitos después del código de país
                    raise NumberParseExceptions("Número inválido")
                return FakePhoneNumber(country_code, national_number)
            found = True

        if not found:
            raise NumberParseExceptions("Código de país no reconocido")

        raise NumberParseExceptions("Número inválido")

    @staticmethod
    def is_valid_number(parsed_number: FakePhoneNumber) -> bool:
        """
        Simula la función phonenumbers.is_valid_number().
        """
        return 1 <= parsed_number.country_code <= 999 and 6 <= len(parsed_number.national_number) <= 12

    @staticmethod
    def is_valid_phone(phone_number: str) -> bool:
        """
        Valida el formato del número telefónico.
        """
        if not phone_number:
            return False

        try:
            parsed_number = PhoneValidator.parse(phone_number)
            return PhoneValidator.is_valid_number(parsed_number)
        except NumberParseException:
            return False

    @staticmethod
    def normalize_phone(phone_number: str, region: Optional[str] = None) -> Optional[str]:
        """
        Normaliza un número telefónico en formato internacional.
        """
        try:
            parsed_number = PhoneValidator.parse(phone_number, region)
            if PhoneValidator.is_valid_number(parsed_number):
                return f"+{parsed_number.country_code}{parsed_number.national_number}"
        except NumberParseException:
            return None

        return None

    @staticmethod
    def get_country_code(phone_number: str, region: Optional[str] = None) -> Optional[str]:
        """
        Obtiene el código de país de un número de teléfono.
        """
        try:
            parsed_number = PhoneValidator.parse(phone_number, region)
            return f"+{parsed_number.country_code}"
        except NumberParseException:
            return None

    @staticmethod
    def format_phone(phone_number: str, format_type: str = 'E164') -> Optional[str]:
        """
        Formatea un número telefónico según el tipo de formato especificado.
        """
        format_mapping = {
            'E164': phonenumbers.PhoneNumberFormat.E164,
            'INTERNATIONAL': phonenumbers.PhoneNumberFormat.INTERNATIONAL,
            'NATIONAL': phonenumbers.PhoneNumberFormat.NATIONAL,
            'RFC3966': phonenumbers.PhoneNumberFormat.RFC3966
        }

        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed_number):
                return phonenumbers.format_number(parsed_number, format_mapping.get(format_type, phonenumbers.PhoneNumberFormat.E164))
        except NumberParseException:
            return None
        
        return None