import json
import logging
from odoo import http
from typing import Dict, Any
from odoo.http import Response, request
from werkzeug.wrappers import Response

_logger = logging.getLogger(__name__)

class ResponseHandler:
    """Handle API response formatting."""
    
    def success_response(self, data: Dict[str, Any], status: int = 200) -> Response:
        """Format successful response."""
        return Response(
            json.dumps({'success': True, **data}),
            content_type='application/json',
            status=status
        )
        
    def error_response(self, message: str, status: int = 400) -> Response:
        """Format error response."""
        return Response(
            json.dumps({'success': False, 'message': message}),
            content_type='application/json',
            status=status
        )
        
    def format_chat_response(self, chat_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format chat information response."""
        if chat_info['chat_id']:
            return {
                'status': 'success',
                'chat_id': chat_info['chat_id'],
                'contact_id': chat_info['contact_id']
            }
        return {
            'status': 'error',
            'message': 'Chat not found'
        }

    """
    Manejador de respuestas HTTP.
    Implementa formatos consistentes de respuesta.
    """

    def success(self, data):
        """Respuesta exitosa."""
        return Response(
            json.dumps(data),
            content_type='application/json',
            status=200
        )

    def error(self, message):
        """Respuesta de error interno."""
        return Response(
            json.dumps({'error': message}),
            content_type='application/json',
            status=500
        )

    def not_found(self, message):
        """Respuesta de recurso no encontrado."""
        return Response(
            json.dumps({'error': message}),
            content_type='application/json',
            status=404
        )

    def bad_request(self, message):
        """Respuesta de solicitud inválida."""
        return Response(
            json.dumps({'error': message}),
            content_type='application/json',
            status=400
        )

    """
    Manejador de respuestas para estandarizar respuestas de API
    """
    
    def build_response(self, data):
        """
        Construye una respuesta estándar.
        
        Args:
            data (dict): Datos a incluir en la respuesta
            
        Returns:
            dict: Respuesta formateada
        """
        response = {'status': 'success'}
        response.update(data)
        _logger.info(f'Returning response: {json.dumps(response)}')
        return response
    
    def build_error_response(self, message):
        """
        Construye una respuesta de error.
        
        Args:
            message (str): Mensaje de error
            
        Returns:
            dict: Respuesta de error formateada
        """
        response = {
            'status': 'error',
            'message': message
        }
        _logger.info(f'Returning response: {json.dumps(response)}')
        return response