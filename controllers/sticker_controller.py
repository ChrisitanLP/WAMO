from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from werkzeug.wrappers import Response
from ..services.controller.sticker_services import StickerService
from ..services.controller.file_services import FileService
from ..utils.validation.request_validator import RequestValidator
from ..utils.response.response import ResponseHandler
from ..utils.log.controller_logger import LoggerController

class MessageStickerController(http.Controller):
    """
    Controlador principal para la gestión de stickers de WhatsApp.
    Implementa el patrón Controller y aplica el principio de Single Responsibility.
    """

    def __init__(self):
        super().__init__()
        self.sticker_service = StickerService()
        self.file_service = FileService()
        self.validator = RequestValidator()
        self.response_handler = ResponseHandler()
        self.logger = LoggerController().get_logger("sticker_controller")

    @http.route('/api/sticker', type='http', auth='public', csrf=False)
    def list_stickers(self):
        """
        Endpoint para listar todos los stickers disponibles.
        Returns:
            Response: JSON con la lista de stickers o error
        """
        try:
            stickers = self.sticker_service.get_all_stickers(request)
            return self.response_handler.success(stickers)
        except Exception as e:
            self.logger.error('Error en list_stickers: %s', str(e))
            return self.response_handler.error(str(e))

    @http.route('/api/sticker/<int:sticker_id>', type='http', auth='public')
    def get_sticker(self, sticker_id):
        """
        Endpoint para obtener un sticker específico.
        Args:
            sticker_id (int): ID del sticker
        Returns:
            Response: JSON con los datos del sticker o error
        """
        try:
            sticker = self.sticker_service.get_sticker_by_id(request, sticker_id)
            return self.response_handler.success(sticker)
        except UserError as e:
            return self.response_handler.not_found(str(e))
        except Exception as e:
            return self.response_handler.error(str(e))

    @http.route('/api/sticker/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_sticker(self, **kwargs):
        """
        Endpoint para crear un nuevo sticker.
        Returns:
            Response: JSON con el ID del sticker creado o error
        """
        try:
            # Validar request
            self.validator.validate_create_request(request)
            
            # Procesar archivo
            file_path = self.file_service.save_sticker_file(
                request.httprequest.files.get('file'),
                request.params.get('file_name')
            )
            
            # Crear sticker
            sticker = self.sticker_service.create_sticker(
                request,
                name=request.params.get('name'),
                file_path=file_path,
                file_name=request.params.get('file_name'),
                mime_type=request.params.get('mime_type'),
                description=request.params.get('description', '')
            )
            
            return self.response_handler.success({'id': sticker.id})
        except ValueError as e:
            return self.response_handler.bad_request(str(e))
        except Exception as e:
            self.logger.error('Error en create_sticker: %s', str(e))
            return self.response_handler.error(str(e))

    @http.route('/api/sticker/delete/<int:sticker_id>', type='http', auth='public', csrf=False)
    def delete_sticker(self, sticker_id):
        """
        Endpoint para eliminar un sticker.
        Args:
            sticker_id (int): ID del sticker a eliminar
        Returns:
            Response: JSON con mensaje de éxito o error
        """
        try:
            self.sticker_service.delete_sticker(request, sticker_id)
            return self.response_handler.success({'message': 'Sticker eliminado exitosamente'})
        except UserError as e:
            return self.response_handler.not_found(str(e))
        except Exception as e:
            return self.response_handler.error(str(e))

    @http.route('/api/sticker/create_default', type='http', auth='public')
    def create_default_stickers(self):
        """
        Endpoint para crear stickers por defecto.
        Returns:
            Response: JSON con mensaje de éxito o error
        """
        try:
            self.sticker_service.create_default_stickers(request)
            return self.response_handler.success({'message': 'Stickers por defecto creados exitosamente'})
        except Exception as e:
            return self.response_handler.error(str(e))