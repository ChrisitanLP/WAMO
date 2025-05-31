import json
from odoo.http import Response
import logging

_logger = logging.getLogger(__name__)

class ResponseBuilder:
    """Clase para construir respuestas HTTP consistentes."""

    def __init__(self):
        self.default_content_type = 'application/json'  # Agregar esta línea
    
    def build_success_response(self, data=None, message='Operación exitosa', status_code=200):
        """
        Construye una respuesta de éxito.
        
        Args:
            data (dict, optional): Datos a incluir en la respuesta
            message (str, optional): Mensaje descriptivo
            status_code (int, optional): Código de estado HTTP
            
        Returns:
            Response: Objeto de respuesta HTTP
        """
        response_data = {
            'status': 'success',
            'message': message
        }
        
        if data:
            response_data['data'] = data
            
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=status_code
        )
        
    def build_error_response(self, message='Ha ocurrido un error', status_code=400, error_code=None):
        """
        Construye una respuesta de error.
        
        Args:
            message (str, optional): Mensaje descriptivo del error
            status_code (int, optional): Código de estado HTTP
            error_code (str, optional): Código de error interno
            
        Returns:
            Response: Objeto de respuesta HTTP
        """
        response_data = {
            'status': 'error',
            'message': message
        }
        
        if error_code:
            response_data['error_code'] = error_code
            
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=status_code
        )

    def _build_response(self, data, content_type=None, status_code=200):
        """
        Construye una respuesta HTTP estandarizada.
        
        Args:
            data (dict): Datos a incluir en la respuesta.
            content_type (str, optional): Tipo de contenido. Default es application/json.
            status_code (int, optional): Código de estado HTTP. Default es 200.
            
        Returns:
            Response: Objeto de respuesta HTTP.
        """
        if content_type is None:
            content_type = self.default_content_type
            
        return Response(
            json.dumps(data),
            content_type=content_type,
            status=status_code
        )
    
    def success(self, message=None, data=None, status_code=200):
        """
        Construye una respuesta de éxito.
        
        Args:
            message (str, optional): Mensaje de éxito.
            data (dict, optional): Datos adicionales.
            status_code (int, optional): Código de estado HTTP. Default es 200.
            
        Returns:
            Response: Objeto de respuesta HTTP.
        """
        response_data = {'status': 'success'}
        
        if message:
            response_data['message'] = message
            
        if data:
            response_data.update(data)
            
        return self._build_response(response_data, status_code=status_code)
    
    def error(self, message, data=None, status_code=400):
        """
        Construye una respuesta de error.
        
        Args:
            message (str): Mensaje de error.
            data (dict, optional): Datos adicionales.
            status_code (int, optional): Código de estado HTTP. Default es 400.
            
        Returns:
            Response: Objeto de respuesta HTTP.
        """
        response_data = {
            'status': 'error',
            'message': message
        }
        
        if data:
            response_data.update(data)
            
        return self._build_response(response_data, status_code=status_code)

    def success_with_data(self, data):
        """
        Build a success response with data.
        
        Args:
            data (dict): Response data
            
        Returns:
            Response: HTTP response with success status and data
        """
        response_data = {
            'status': 'success',
            **data
        }
        return Response(json.dumps(response_data), content_type='application/json')
        
    def error_with_data(self, message, data):
        """
        Build an error response with a message and additional data.
        
        Args:
            message (str): Error message
            data (dict): Additional data
            
        Returns:
            Response: HTTP response with error status and data
        """
        response_data = {
            'status': 'error',
            'message': message,
            **data
        }
        return Response(json.dumps(response_data), content_type='application/json')

    def exception(self, exception, status_code=500):
        """
        Construye una respuesta a partir de una excepción.
        
        Args:
            exception (Exception): Excepción capturada
            status_code (int): Código de estado HTTP
            
        Returns:
            Response: Objeto de respuesta HTTP
        """
        _logger.error(f"Excepción capturada: {str(exception)}", exc_info=True)
        
        response_data = {
            'status': 'error',
            'message': str(exception)
        }
        
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=status_code
        )
        
    def not_found(self, message="Recurso no encontrado"):
        """
        Construye una respuesta para recursos no encontrados.
        
        Args:
            message (str): Mensaje personalizado
            
        Returns:
            Response: Objeto de respuesta HTTP
        """
        return self.error(message, 404)
        
    def validation_error(self, message="Error de validación", errors=None):
        """
        Construye una respuesta para errores de validación.
        
        Args:
            message (str): Mensaje principal
            errors (dict): Errores de validación detallados
            
        Returns:
            Response: Objeto de respuesta HTTP
        """
        response_data = {
            'status': 'error',
            'message': message
        }
        
        if errors:
            response_data['errors'] = errors
            
        return Response(
            json.dumps(response_data),
            content_type='application/json',
            status=errors
        )