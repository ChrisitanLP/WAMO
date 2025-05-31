
import re

"""Clase para validar codigo de colores."""
class ColorValidator:
    staticmethod
    def is_valid_color(color: str) -> bool:
        """
        Validate color format (hex, rgb, rgba).
        
        Args:
            color (str): Color to validate
        
        Returns:
            bool: Whether color is valid
        """
        hex_pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        rgb_pattern = r'^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$'
        rgba_pattern = r'^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(0|1|0\.\d+)\s*\)$'
        
        return (re.match(hex_pattern, color) is not None or
                re.match(rgb_pattern, color) is not None or
                re.match(rgba_pattern, color) is not None)

    @staticmethod
    def normalize_color(color: str) -> str:
        """
        Normalize color to hex format.
        
        Args:
            color (str): Color to normalize
        
        Returns:
            str: Normalized hex color
        """
        if re.match(r'^#([A-Fa-f0-9]{3}){1,2}$', color):
            return color.upper()
        return color