import json
from odoo import http
from odoo.http import request, Response
from ..services.controller.product_service import ProductService
from ..utils.response.response import ResponseHandler
from ..utils.response.builder import ResponseBuilder
from ..utils.validation.product_validator import ProductValidator
from ..utils.log.controller_logger import LoggerController

class MessageProductController(http.Controller):
    def __init__(self):
        super().__init__()
        self.product_service = ProductService()
        self.response_handler = ResponseHandler()
        self.validator = ProductValidator()
        self.response_builder = ResponseBuilder()
        self.logger = LoggerController().get_logger("product_controller")

    @http.route('/api/products', auth='public', website=True)
    def list_products(self, **kwargs):
        """Render products list template with pagination and filtering."""
        try:
            # Ensure default values when parameters are missing or invalid
            try:
                page = int(kwargs.get('page', 1)) if kwargs.get('page') else 1
            except (ValueError, TypeError):
                page = 1
                
            try:
                limit = int(kwargs.get('limit', 20)) if kwargs.get('limit') else 20
            except (ValueError, TypeError):
                limit = 20
                
            search = kwargs.get('search', '')
            
            products = self.product_service.get_products(
                page=page,
                limit=limit,
                search=search
            )
            
            return request.render(
                'message_app.products_template',
                {
                    'products': products,
                    'page': page,
                    'limit': limit,
                    'search': search
                }
            )
        except Exception as e:
            self.logger.error(f"Error in list_products: {str(e)}")
            return self.response_handler.error(e)

    @http.route('/api/info_products', type='json', auth='public', website=False)
    def api_list_products(self, **kwargs):
        """API endpoint for product listing with filtering and pagination."""
        try:
            self.validator.validate_product_request(kwargs)
            
            filters = self._build_filters(kwargs)
            products = self.product_service.get_products_json(**filters)
            
            return self.response_handler.success(products)
        except Exception as e:
            return self.response_handler.error(e)

    def _build_filters(self, kwargs):
        """Build filter dictionary from request parameters."""
        return {
            'page': int(kwargs.get('page', 1)),
            'limit': int(kwargs.get('limit', 20)),
            'search': kwargs.get('search', ''),
            'category_id': kwargs.get('category_id'),
            'min_price': kwargs.get('min_price'),
            'max_price': kwargs.get('max_price')
        }

    @http.route('/api/products/search', type='http', auth='public', csrf=False)
    def search_products(self, query=""):
        """Search products by name."""
        try:
            products_data = self.product_service.search_products(query)
            # Use Response object with proper JSON structure matching the original format
            response_data = {
                'status': 'success',
                'products': products_data  # Keep 'products' key as in original
            }
            return Response(json.dumps(response_data), content_type='application/json')
        except Exception as e:
            self.logger.error(f"Error searching products: {e}", exc_info=True)
            response_data = {
                'status': 'error',
                'message': str(e)
            }
            return Response(json.dumps(response_data), content_type='application/json')