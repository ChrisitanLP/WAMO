# utils/image_handler.py
import requests
import base64
from ..log.setup_logger import setup_logger

logger = setup_logger(__name__)

class ImageHandler:
    """Handler for image-related operations."""

    @staticmethod
    def download_and_convert_image(url):
        """Download image from URL and convert to base64."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return base64.b64encode(response.content).decode('utf-8')
            logger.warning(f'Failed to download image: {url}')
            return None
        except Exception as e:
            logger.error(f'Error processing image: {e}')
            return None