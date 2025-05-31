from typing import Dict, List, Optional, Any
from odoo.exceptions import UserError
from odoo.http import request
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class ConnectionService:
    """Service for managing WhatsApp connections."""

    def __init__(self, env=None):
        """
        Initialize the connection service.
        
        Args:
            env: Odoo environment (optional)
        """
        self.env = env or request.env
        self.logger = ExtraLoggerConfig().get_logger("connection_services")
    
    def get_all_connections(self, as_dict=True):
        """
        Retrieve all WhatsApp connections.
        
        Returns:
            List of connection dictionaries
        """
        try:
            connections = self.env['message_app.message_connection'].search([])
            if as_dict:
                return [
                    {
                        'id': conn.id,
                        'name': conn.name,
                        'phone_number': conn.phone_number,
                        'color': conn.color,
                        'active': conn.active
                    } 
                    for conn in connections
                ]
            else:
                return connections
        except Exception as e:
            self.logger.error(f"Error retrieving connections: {e}", exc_info=True)
            raise UserError("Could not retrieve connections")
            
    def create_connection(self, data: Dict[str, Any]) -> Any:
        """
        Create a new WhatsApp connection.
        
        Args:
            data: Connection creation data
        
        Returns:
            Created connection record
        """
        try:
            connection_model = self.env['message_app.message_connection'].sudo()
            connection = connection_model.add_connection(
                name=data['name'], 
                phone_number=data['phone_number'], 
                color=data.get('color')
            )
            return connection
        except Exception as e:
            self.logger.error(f"Error creating connection: {e}", exc_info=True)
            raise UserError(f"Failed to create connection: {e}")
        
    def delete_connection(self, connection_id: int) -> bool:
        """
        Delete a WhatsApp connection.
        
        Args:
            connection_id: ID of connection to delete
        
        Returns:
            Boolean indicating success
        """
        try:
            connection_model = self.env['message_app.message_connection']
            connection = connection_model.browse(connection_id)
            
            if not connection.exists():
                raise UserError(f"Connection with ID {connection_id} not found")
            
            return connection.delete_connection(connection_id)
        except Exception as e:
            self.logger.error(f"Error deleting connection {connection_id}: {e}", exc_info=True)
            raise UserError(f"Failed to delete connection: {e}")
        
    def prepare_connection_data(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare connection data for creation.
        
        Args:
            kwargs: Incoming connection data
        
        Returns:
            Prepared connection data dictionary
        """
        try:
            return {
                'name': kwargs.get('name'),
                'phone_number': kwargs.get('phone_number'),
                'color': kwargs.get('color', '#cccccc')
            }
        except Exception as e:
            self.logger.error(f"Error preparing connection data: {e}", exc_info=True)
            raise UserError("Could not prepare connection data")