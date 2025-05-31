import json
from odoo import http
from odoo.http import request, Response
from ..services.controller.contact_services import ContactService
from ..services.controller.product_service import ProductService
from ..utils.validation.payload_validator import PayloadValidator
from ..utils.response.builder import ResponseBuilder
from ..utils.log.controller_logger import LoggerController

class MessageContactController(http.Controller):
    """Controller for handling WhatsApp contact-related operations."""
    
    def __init__(self):
        super().__init__()
        self.contact_service = ContactService()
        self.product_service = ProductService()
        self.validator = PayloadValidator()
        self.response_builder = ResponseBuilder()
        self.logger = LoggerController().get_logger("contact_controller")

    @http.route('/api/contacts/search', type='http', auth='public', csrf=False)
    def search_contacts(self, query=""):
        """Search WhatsApp contacts based on name or phone number."""
        try:
            contacts_data = self.contact_service.search_contacts(query)
            response_data = {
                'status': 'success',
                'contacts': contacts_data  # Use 'contacts' key instead of 'data'
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            self.logger.error(f"Error searching contacts: {e}")
            response_data = {
                'status': 'error',
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')

    @http.route('/api/contacts/save', type='json', auth='public', methods=['POST'], csrf=False)
    def save_contact(self):
        """Save a new WhatsApp contact."""
        try:
            payload = request.httprequest.get_json() or {}
            if not isinstance(payload, dict):  # Validación adicional
                return self.response_builder.build_error_response("Invalid JSON payload")
            
            validation_result = self.validator.validate_contact_payload(payload)
            if not validation_result.is_valid:
                return self.response_builder._build_error_response(validation_result.message)

            result = self.contact_service.save_contact(payload)
            return self.response_builder._build_success_response(result)
        except Exception as e:
            self.logger.error(f"Error saving contact: {e}")
            return self.response_builder._build_error_response(str(e))

    @http.route('/api/contact/add', type='json', auth='public', methods=['POST'])
    def add_contact(self):
        """Add a new contact to the system."""
        try:
            payload = request.httprequest.get_json() or {}
            if not isinstance(payload, dict):  # Validación adicional
                return self.response_builder.build_error_response("Invalid JSON payload")

            validation_result = self.validator.validate_new_contact_payload(payload)
            if not validation_result.is_valid:
                return self.response_builder._build_error_response(validation_result.message)

            result = self.contact_service.add_contact(payload)

            if result.get('status') == 'error':
                return self.response_builder._build_error_response(result)
            else:
                return self.response_builder._build_success_response(result)
        except Exception as e:
            self.logger.error(f"Error adding contact: {e}")
            return self.response_builder._build_error_response(str(e))
