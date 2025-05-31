import odoo
import requests
from odoo.http import request
from odoo.exceptions import UserError
from ..utils.log.extra_logger_config import ExtraLoggerConfig
from datetime import datetime
from functools import lru_cache

# Cache configuration
CACHE_TIMEOUT = 300  # 5 minutes

class APIConfig:
    """Manage API configuration."""

    def __init__(self):
        """Inicializa la configuración de logs usando ExtraLoggerConfig."""
        self.logger = ExtraLoggerConfig().get_logger("api_config")

    @property
    def base_url(self):
        if not self._base_url:
            self._base_url = self.get_api_url()
        return self._base_url

    def _get_cache_key(self) -> str:
        """Generar una clave de caché única basada en la empresa y la hora actual."""
        try:
            company_id = request.env['ir.config_parameter'].sudo().get_param('company_code')
            
            if not company_id:
                raise UserError("Clave de caché única no está configurada en los parámetros del sistema.")
            
            timestamp = datetime.now().strftime('%Y%m%d%H')
            return f'api_url_company_{company_id}_{timestamp}'
            
        except Exception as e:
            self.logger.error("Error al recuperar la clave de caché única: %s", str(e))
            raise UserError("No se pudo recuperar la clave de caché única. Verifique la configuración del sistema.") from e

    def get_api_url(self):
        """Retrieves API URL from system parameters."""
        try:
            # Try to get the API URL directly from the environment if available
            if hasattr(self, 'env'):
                api_url = self.env['ir.config_parameter'].sudo().get_param('url_api')
            elif hasattr(self, '_cr'):
                # If we have a cursor but no env, create a new env
                from odoo import api
                env = api.Environment(self._cr, odoo.SUPERUSER_ID, {})
                api_url = env['ir.config_parameter'].sudo().get_param('url_api')
            else:
                # Fall back to request.env if available
                try:
                    api_url = request.env['ir.config_parameter'].sudo().get_param('url_api')
                except RuntimeError:
                    # Create a new environment if request is not available
                    from odoo import api, registry
                    db_name = odoo.tools.config['db_name']
                    with registry(db_name).cursor() as cr:
                        env = api.Environment(cr, odoo.SUPERUSER_ID, {})
                        api_url = env['ir.config_parameter'].sudo().get_param('url_api')
            
            if not api_url:
                raise UserError("API URL is not configured in system parameters.")
            return api_url
        except Exception as e:
            self.logger.error(f"Error getting API URL: {e}")
            raise UserError("Could not retrieve API URL. Please verify system configuration.")

    @lru_cache(maxsize=128)
    def _get_api_url(self) -> str:
        """
        Obtener la URL de la API con almacenamiento en caché, usando una clave única.
        """
        try:
            cache_key = self._get_cache_key()
            api_url = request.env['ir.config_parameter'].sudo().get_param(cache_key)

            if not api_url:
                api_url = request.env['ir.config_parameter'].sudo().get_param('url_api')
                if not api_url:
                    raise UserError("La URL de la API no está configurada en los parámetros del sistema.")
                request.env['ir.config_parameter'].sudo().set_param(cache_key, api_url)

            return str(api_url).rstrip('/')
        except Exception as e:
            self.logger.error("Error al recuperar la URL de la API: %s", str(e))
            raise UserError("No se pudo recuperar la URL de la API. Verifique la configuración del sistema.") from e

    def make_request(self, endpoint, data, method='POST'):
        """
        Realiza una solicitud HTTP a la API.
        
        Args:
            endpoint (str): Endpoint de la API
            data (dict): Datos a enviar
            method (str): Método HTTP (POST, GET, DELETE)
            
        Returns:
            dict: Respuesta de la API
        """
        api_url = f"{self.get_api_url()}/{endpoint}"
        
        try:
            self.logger.info(f"Enviando solicitud {method} a {api_url}")
            self.logger.debug(f"Datos: {data}")
            
            if method.upper() == 'GET':
                response = requests.get(api_url, params=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(api_url, json=data)
            else:
                response = requests.post(api_url, json=data)
                
            response.raise_for_status()
            response_data = response.json()
            
            self.logger.info(f"Respuesta recibida de {endpoint}: {response.status_code}")
            self.logger.debug(f"Datos de respuesta: {response_data}")
            
            return response_data
            
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"Error HTTP: {http_err}")
            try:
                error_data = response.json()
                return error_data
            except:
                return {"success": False, "message": f"Error HTTP: {http_err}"}
                
        except requests.exceptions.ConnectionError as conn_err:
            self.logger.error(f"Error de conexión: {conn_err}")
            return {"success": False, "message": "Error de conexión con la API externa."}
            
        except requests.exceptions.Timeout as timeout_err:
            self.logger.error(f"Tiempo de espera agotado: {timeout_err}")
            return {"success": False, "message": "Tiempo de espera agotado al conectar con la API externa."}
            
        except requests.exceptions.RequestException as req_err:
            self.logger.error(f"Error en la solicitud: {req_err}")
            return {"success": False, "message": f"Error en la solicitud: {req_err}"}
            
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            return {"success": False, "message": f"Error inesperado: {e}"}