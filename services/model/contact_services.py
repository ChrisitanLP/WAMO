import requests
from typing import List, Dict, Any, Optional, Union
from odoo.exceptions import UserError
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class ContactService:
    """Servicio para manejar la comunicación con la API externa de contactos."""

    def __init__(self):
        self.api_client = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("contact_service")

    def get_contacts(self, params) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Makes a GET request to the contacts endpoint.
        
        Args:
            params: Dictionary with parameters for the API request
            
        Returns:
            List of contact dictionaries or dictionary with contacts and pagination info
        """
        try:
            api_url = self.api_client.get_api_url()
            self.logger.info(f"Fetching contacts from {api_url} with params: {params}")
            
            response = requests.get(
                f'{api_url}/getContacts',
                params=params,
                timeout=30  # Aumentado el timeout para permitir respuestas más grandes
            )

            if response.status_code != 200:
                self.logger.error(f"Error en la API: {response.status_code} - {response.text}")
                raise UserError(f"Error al obtener la información de contactos: {response.status_code}")

            response.raise_for_status()
            
            # Validate response format
            data = response.json()
            
            # Check if we received a dictionary with 'contacts' key and pagination info
            if isinstance(data, dict):
                # Validar que el diccionario tiene la estructura esperada
                if 'contacts' in data:
                    contacts = data['contacts']
                    if not isinstance(contacts, list):
                        self.logger.error(f"Invalid contacts format: expected list, got {type(contacts)}")
                        raise UserError("Invalid data format from API: 'contacts' is not a list")
                    
                    # Si tiene información de paginación, devolver todo el diccionario
                    if any(key in data for key in ['totalPages', 'currentPage', 'totalItems']):
                        return data
                    # Si solo tiene la lista de contactos, devolver solo esa lista
                    return contacts
                # Si es un diccionario pero no tiene la clave 'contacts'
                elif 'data' in data and isinstance(data['data'], list):
                    return data['data']
                else:
                    self.logger.error(f"Unexpected API response dictionary format without contacts key")
                    self.logger.debug(f"API response content: {data}")
                    raise UserError("Unexpected data structure received from API")
            
            # Check if we received a list directly
            elif isinstance(data, list):
                return data
                
            # Otherwise, log the error and raise an exception
            else:
                self.logger.error(f"Unexpected API response format: {type(data)}")
                self.logger.debug(f"API response content: {data}")
                raise UserError("Unexpected data format received from API")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise UserError(f"Failed to communicate with the API: {str(e)}")
        except ValueError as e:
            self.logger.error(f"Invalid JSON response: {e}")
            raise UserError(f"Invalid response format from API: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error in contact service: {e}", exc_info=True)
            raise UserError(f"Failed to process contacts: {str(e)}")