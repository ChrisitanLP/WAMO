import re

class ProductValidator:
    """Clase para validar los parámetros de las solicitudes de productos."""
    
    def validate_product_request(self, params):
        """Valida los parámetros de la solicitud de productos."""
        errors = []
        
        # Validar que la paginación sea un número entero positivo
        if 'page' in params and (not params['page'].isdigit() or int(params['page']) < 1):
            errors.append("El parámetro 'page' debe ser un número entero positivo.")
        
        if 'limit' in params and (not params['limit'].isdigit() or int(params['limit']) < 1):
            errors.append("El parámetro 'limit' debe ser un número entero positivo.")
        
        # Validar que los precios sean valores numéricos positivos
        if 'min_price' in params and (not self._is_valid_price(params['min_price'])):
            errors.append("El parámetro 'min_price' debe ser un número válido.")
        
        if 'max_price' in params and (not self._is_valid_price(params['max_price'])):
            errors.append("El parámetro 'max_price' debe ser un número válido.")
        
        # Validar que el texto de búsqueda no contenga caracteres peligrosos
        if 'search' in params and not self._is_valid_search(params['search']):
            errors.append("El parámetro 'search' contiene caracteres no permitidos.")
        
        if errors:
            raise ValueError("Error en la validación de parámetros: " + "; ".join(errors))
    
    def _is_valid_price(self, value):
        """Valida si un valor es un número positivo válido."""
        try:
            return float(value) >= 0
        except ValueError:
            return False
    
    def _is_valid_search(self, value):
        """Valida que la cadena de búsqueda no tenga caracteres peligrosos."""
        return bool(re.match(r'^[a-zA-Z0-9\s]*$', value))
