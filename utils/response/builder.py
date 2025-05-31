import json
from odoo.http import Response

class ResponseBuilder:
    """Builder for API responses."""

    def build_success_response(self, data, message="Success"):
        """Build a success response."""
        response_data = {
            'status': 'success',
            'data': data,
            'message': message
        }
        return Response(json.dumps(response_data), content_type='application/json')

    def build_error_response(self, message, status_code=400):
        """Build an error response."""
        response_data = {
            'status': 'error',
            'message': str(message)
        }
        return Response(json.dumps(response_data), 
                       content_type='application/json', 
                       status=status_code)

    def _build_success_response(self, data, message="Success"):
        """Build a success response."""
        response_data = {
            'status': 'success',
            'data': data,
            'message': message
        }
        return response_data

    def _build_error_response(self, data, message="Error"):
        """Build a success response."""
        response_data = {
            'status': 'error',
            'data': data,
            'message': message
        }
        return response_data

    