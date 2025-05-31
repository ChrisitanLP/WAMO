# models/sticker_storage.py
import os
import shutil
from odoo.exceptions import UserError
from ..utils.log.extra_logger_config import ExtraLoggerConfig

class StickerStorage:
    """
    Clase para gestionar el almacenamiento físico de stickers.
    Implementa el patrón Strategy para el almacenamiento.
    """
    
    STICKER_DIR = 'message_app/static/src/assets/img/stickers'
    
    def __init__(self):
        self.logger = ExtraLoggerConfig().get_logger("sticker_storage")

    def store_sticker_file(self, source_path, file_name):
        """
        Almacena un archivo de sticker en el directorio correspondiente.
        
        Args:
            source_path (str): Ruta del archivo fuente
            file_name (str): Nombre del archivo
            
        Returns:
            str: URL del sticker almacenado
            
        Raises:
            UserError: Si hay un error al almacenar el archivo
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(self.STICKER_DIR, exist_ok=True)
            
            # Construir la ruta de destino
            destination_path = os.path.join(self.STICKER_DIR, file_name)
            
            # Copiar el archivo
            shutil.copy2(source_path, destination_path)
            self.logger.info(f"Sticker file stored successfully: {destination_path}")
            # Retornar la URL del sticker
            return f'/{self.STICKER_DIR}/{file_name}'
            
        except Exception as e:
            self.logger.error(f"Error storing sticker file {file_name}: {str(e)}", exc_info=True)
            raise UserError(f"Error storing sticker file: {str(e)}")
            
    def remove_sticker_file(self, file_name):
        """
        Elimina un archivo de sticker.
        
        Args:
            file_name (str): Nombre del archivo a eliminar
            
        Raises:
            UserError: Si hay un error al eliminar el archivo
        """
        try:
            file_path = os.path.join(self.STICKER_DIR, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Sticker file removed successfully: {file_name}")
            else:
                self.logger.warning(f"Sticker file not found: {file_name}")
        except Exception as e:
            self.logger.error(f"Error removing sticker file {file_name}: {str(e)}", exc_info=True)
            raise UserError(f"Error removing sticker file: {str(e)}")
