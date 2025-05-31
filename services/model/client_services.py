import requests
from typing import Dict, Any
from odoo.exceptions import UserError
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class ClientService:
    """Service for handling WhatsApp API operations."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("client_services")
        
    def register_client(self, phone_number: str) -> Dict[str, Any]:
        """Register a new client with the WhatsApp API."""
        try:
            response = requests.post(
                f"{self.api_config.get_api_url()}/addClient",
                json={'number': phone_number},
                timeout=30
            )
            response.raise_for_status()
            self.logger.info(f"Client {phone_number} registered successfully.")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"API communication error while registering client: {str(e)}", exc_info=True)
            raise UserError(f"API communication error: {str(e)}")
            
    def remove_client(self, phone_number: str) -> Dict[str, Any]:
        """Remove a client from the WhatsApp API."""
        try:
            response = requests.post(
                f"{self.api_config.get_api_url()}/removeClient",
                json={'number': phone_number},
                timeout=10
            )
            response.raise_for_status()
            self.logger.info(f"Client {phone_number} removed successfully.")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"API communication error while removing client: {str(e)}", exc_info=True)
            raise UserError(f"API communication error: {str(e)}")
