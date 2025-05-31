from typing import List, Dict, Any
from odoo.http import request
from odoo.exceptions import UserError
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class StickerService:
    """
    Servicio para la gestión de stickers.
    Implementa la lógica de negocio relacionada con los stickers.
    """

    def __init__(self):
        self.logger = ExtraLoggerConfig().get_logger("sticker_storage")

    def get_all_stickers(self, request) -> List[Dict[str, Any]]:
        """
        Obtiene todos los stickers activos.
        Args:
            request: Objeto request de Odoo
        Returns:
            list: Lista de stickers con sus datos
        """
        try:
            stickers = request.env['message_app.message_sticker'].search([])
            return self._format_sticker_list(request, stickers)
        except Exception as e:
            self.logger.error(f"Error al obtener stickers: {str(e)}", exc_info=True)
            raise UserError("No se pudieron obtener los stickers.")

    def get_sticker_by_id(self, request, sticker_id: int) -> Dict[str, Any]:
        """
        Obtiene un sticker por su ID.
        Args:
            request: Objeto request de Odoo
            sticker_id (int): ID del sticker
        Returns:
            dict: Datos del sticker
        Raises:
            UserError: Si el sticker no existe
        """
        try:
            sticker = request.env['message_app.message_sticker'].browse(sticker_id)
            if not sticker.exists():
                self.logger.warning(f"Intento de acceso a sticker inexistente: ID {sticker_id}")
                raise UserError("El sticker no existe.")
            return sticker.read(['id', 'name', 'sticker_file', 'file_name', 'mime_type', 'description'])[0]
        except Exception as e:
            self.logger.error(f"Error al obtener sticker {sticker_id}: {str(e)}", exc_info=True)
            raise UserError("No se pudo recuperar el sticker.")

    def create_sticker(self, request, **kwargs) -> Any:
        """
        Crea un nuevo sticker.
        Args:
            request: Objeto request de Odoo
            **kwargs: Datos del sticker
        Returns:
            record: Registro del sticker creado
        """
        try:
            return request.env['message_app.message_sticker'].add_sticker(**kwargs)
        except Exception as e:
            self.logger.error(f"Error al crear sticker: {str(e)}", exc_info=True)
            raise UserError("No se pudo crear el sticker.")

    def delete_sticker(self, request, sticker_id: int) -> None:
        """
        Elimina un sticker.
        Args:
            request: Objeto request de Odoo
            sticker_id (int): ID del sticker
        Raises:
            UserError: Si el sticker no existe
        """
        try:
            sticker = request.env['message_app.message_sticker'].browse(sticker_id)
            if not sticker.exists():
                self.logger.warning(f"Intento de eliminación de sticker inexistente: ID {sticker_id}")
                raise UserError("El sticker no existe.")
            sticker.delete_sticker()
            self.logger.info(f"Sticker eliminado correctamente: ID {sticker_id}")
        except Exception as e:
            self.logger.error(f"Error al eliminar sticker {sticker_id}: {str(e)}", exc_info=True)
            raise UserError("No se pudo eliminar el sticker.")

    def create_default_stickers(self, request) -> None:
        """
        Crea los stickers por defecto.
        Args:
            request: Objeto request de Odoo
        """
        try:
            request.env['message_app.message_sticker'].create_default_stickers_model()
            self.logger.info("Stickers por defecto creados exitosamente.")
        except Exception as e:
            self.logger.error(f"Error al crear stickers por defecto: {str(e)}", exc_info=True)
            raise UserError("No se pudieron crear los stickers por defecto.")

    def _format_sticker_list(self, request, stickers) -> List[Dict[str, Any]]:
        """
        Formatea la lista de stickers para la respuesta.
        Args:
            request: Objeto request de Odoo
            stickers: Recordset de stickers
        Returns:
            list: Lista formateada de stickers
        """
        sticker_data = []
        for sticker in stickers:
            try:
                sticker_info = sticker.read(['id', 'name', 'file_name', 'sticker_url', 'mime_type', 'description'])[0]
                if sticker_info.get('sticker_url'):
                    sticker_info['sticker_url'] = request.httprequest.host_url + sticker_info['sticker_url']
                    sticker_data.append(sticker_info)
                else:
                    self.logger.warning(f"Sticker sin URL: {sticker_info.get('name')}")
            except Exception as e:
                self.logger.error(f"Error formateando sticker {sticker.id}: {str(e)}", exc_info=True)
        return sticker_data