import requests
from typing import List, Dict, Any
from odoo.exceptions import UserError
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class UserService:
    """Servicio para manejar la comunicación con la API externa de usuarios."""

    def __init__(self):
        self.api_client = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("user_services")

    def get_account_info(self) -> List[Dict[str, Any]]:
        """
        Obtiene la información de los usuarios autenticados desde la API.
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con la información de los usuarios.
        """
        try:
            api_url = self.api_client.get_api_url()
            response = requests.get(f"{api_url}/authenticated-accounts", timeout=10)

            if response.status_code != 200:
                self.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                raise UserError(f"Error al obtener la información de cuentas: {response.status_code}")

            return response.json().get('accounts', [])

        except requests.RequestException as e:
            self.logger.error(f"Error de comunicación con la API: {str(e)}", exc_info=True)
            raise UserError("Error de comunicación con la API.")
