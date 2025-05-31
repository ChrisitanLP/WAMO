from odoo.exceptions import ValidationError
from odoo.http import request
from typing import List, Dict, Any
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class ProductService:
    FIELDS_TO_FETCH = [
        'id', 'name', 'list_price', 'description', 
        'default_code', 'type', 'qty_available', 
        'image_1920'
    ]

    def __init__(self):
        self.logger = ExtraLoggerConfig().get_logger("product_services")

    def get_products(self, page=1, limit=20, search='', **kwargs) -> List[Dict[str, Any]]:
        """Get paginated and filtered products."""
        domain = self._build_domain(search, **kwargs)
        offset = (page - 1) * limit
        
        products = request.env['product.product'].search(
            domain,
            limit=limit,
            offset=offset,
            order='name asc'
        )

        return [
            {
                'id': product.id, 
                'name': product.name, 
                'list_price': product.list_price,
                'description': product.description,
                'default_code': product.default_code,
                'type': product.type,
                'image_1920': product.image_1920
            }
            for product in products
        ]
    def get_products_json(self, **kwargs) -> Dict[str, Any]:
        """Get products in JSON format with additional metadata."""
        products = self.get_products(**kwargs)
        total_count = self._get_total_count(kwargs)
        
        return {
            'data': products,
            'total': total_count,
            'page': kwargs.get('page', 1),
            'limit': kwargs.get('limit', 20)
        }

    def _get_total_count(self, kwargs) -> int:
        """Get total count of products without pagination."""
        domain = self._build_domain(kwargs.get('search', ''), **kwargs)
        return request.env['product.product'].search_count(domain)

    def _build_domain(self, search, **kwargs) -> List[tuple]:
        """Build search domain based on filters."""
        domain = []  # Asegurar que siempre es una lista
        
        if search:
            domain += [
                '|', '|',
                ('name', 'ilike', search),
                ('default_code', 'ilike', search),
                ('description', 'ilike', search)
            ]
            
        if kwargs.get('category_id'):
            domain.append(('categ_id', '=', kwargs['category_id']))
            
        if kwargs.get('min_price'):
            domain.append(('list_price', '>=', float(kwargs['min_price'])))
            
        if kwargs.get('max_price'):
            domain.append(('list_price', '<=', float(kwargs['max_price'])))
        
        return domain 

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search for products by name."""
        try:
            domain = [('name', 'ilike', query)]
            products = request.env['product.template'].search(domain)
            
            # Return product data with consistent structure
            return [{
                'id': product.id,
                'name': product.name,
                'list_price': product.list_price,
                'image_url': f'/web/image/product.template/{product.id}/image_1920'
            } for product in products]
        except Exception as e:
            self.logger.error(f"Error searching products: {e}", exc_info=True)
            return []