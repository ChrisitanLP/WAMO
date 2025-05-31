import requests
from typing import Dict, List, Any, Union
from odoo.http import request
from odoo.exceptions import UserError
from ...utils.log.extra_logger_config import ExtraLoggerConfig
from ...config.api_config import APIConfig

class ChatService:
    """Service for managing WhatsApp chats."""
    
    def __init__(self, env = None):
        """
        Initialize the ChatService with an optional environment.
        
        Args:
            env: Odoo environment, can be None for API-only operations
        """
        self.env = env
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("chat_services")

    def get_chat_info(self, data, env=None) -> Dict[str, Any]:
        """Retrieve chat and contact information."""
        env = env or request.env
            
        try:
            domain = self._build_chat_domain(data)
            
            chat = self.env['message_app.message_chat'].search(domain, limit=1)
            contact = self.env['message_app.message_contact'].search(domain, limit=1)
            
            return {
                'chat_id': chat.id if chat else None,
                'contact_id': contact.id if contact else None
            }
        except Exception as e:
            self.logger.error(f"Error retrieving chat info: {e}", exc_info=True)
            raise UserError("Failed to retrieve chat information.")
        
    def _build_chat_domain(self, data: Dict[str, Any]) -> List[tuple]:
        """Build domain filter for chat search."""
        return [
            ('serialized', '=', data.get('serialized')),
            ('user_id', '=', data.get('user_id')),
            ('phone_number', '=', data.get('phone_number'))
        ]

    def get_unread_chats(self, page=1, last_sync=None) -> Union[List, Dict]:
        """
        Fetches unread chats from the API with pagination support.
        
        Args:
            page: Page number to fetch
            last_sync: Last synchronization timestamp
            
        Returns:
            List or Dict of chat data from API, depending on API response format
        """
        try:
            params = {'page': page}
            if last_sync:
                params['last_sync'] = last_sync

            api_url = self.api_config.get_api_url()
            self.logger.info(f"Fetching unread chats from {api_url} with params: {params}")
            
            response = requests.get(
                f'{api_url}/unreadChats',
                params=params,
                timeout=10
            )

            response.raise_for_status()
            
            # Verificar el tipo de contenido para determinar si esperar JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                self.logger.warning(f"API returned non-JSON content type: {content_type}")
                
            # Intentar analizar como JSON, manejar errores
            try:
                chat_data = response.json()
            except ValueError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                raise UserError(f"Invalid API response format: {str(e)}")
            
            # Validar que la respuesta no sea None
            if chat_data is None:
                self.logger.warning("API returned null response")
                return []
                
            # Log de información sobre la estructura de respuesta
            if isinstance(chat_data, dict):
                self.logger.info(f"API returned dictionary with keys: {list(chat_data.keys())}")
                
                # Check if we're beyond the last page
                if (chat_data.get('totalPages', 0) < page or 
                    (isinstance(chat_data.get('unreadChats'), list) and len(chat_data.get('unreadChats', [])) == 0)):
                    self.logger.info(f"Page {page} is beyond available data (total pages: {chat_data.get('totalPages', 0)})")
                    return []  # Return empty list instead of raising an error
            elif isinstance(chat_data, list):
                self.logger.info(f"API returned list with {len(chat_data)} items")
                if len(chat_data) == 0:
                    self.logger.info(f"Page {page} returned an empty list")
                    return []
            else:
                self.logger.warning(f"API returned unexpected data type: {type(chat_data)}")

            # Only schedule async load if we have a valid environment and there are more pages
            if page == 1 and self.env is not None:
                current_page = chat_data.get('currentPage', 1) if isinstance(chat_data, dict) else 1
                total_pages = chat_data.get('totalPages', 1) if isinstance(chat_data, dict) else 1
                
                if current_page < total_pages:
                    try:
                        self._schedule_async_load(2)
                    except Exception as e:
                        # Log the error but don't raise it to avoid interrupting main sync
                        self.logger.warning(f"Async chat loading could not be scheduled: {e}")
            
            return chat_data
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}", exc_info=True)
            raise UserError(f"Failed to fetch unread chats due to API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching unread chats: {e}", exc_info=True)
            raise UserError(f"Failed to fetch unread chats: {str(e)}")

    def _schedule_async_load(self, start_page: int) -> None:
        """
        Schedules asynchronous loading of additional pages.
        
        Args:
            start_page: Starting page number for additional loads
        
        Raises:
            UserError: If scheduling fails
        """
        if not self.env:
            self.logger.error("Cannot schedule async load: environment not available")
            raise UserError("Service environment not initialized properly.")
            
        try:
            # Get model reference using direct search instead of env.ref
            model = self.env['ir.model'].sudo().search([
                ('model', '=', 'message_app.message_chat')
            ], limit=1)
            
            if not model:
                self.logger.error("Model 'message_app.message_chat' not found in ir.model")
                return  # Skip scheduling without raising error

            # Create scheduled action (cron job)
            self.env['ir.cron'].sudo().create({
                'name': f'Load WhatsApp Chats (Page {start_page})',
                'model_id': model.id,
                'state': 'code',
                'code': f'model._load_chats_async({start_page})',
                'interval_type': 'minutes',
                'interval_number': 1,
                'numbercall': 1,  # Run only once
                'active': True,
                'user_id': self.env.user.id
            })
            self.logger.info(f"Successfully scheduled async chat load for page {start_page}")
        except Exception as e:
            self.logger.error(f"Error scheduling async chat load: {e}", exc_info=True)
            raise UserError(f"Failed to schedule asynchronous chat loading: {str(e)}")