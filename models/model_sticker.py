# models/message_sticker.py
import os
from odoo import models, fields, api
from odoo.exceptions import UserError
from .mixins.loggable import LoggableMixin
from ..utils.validation.sticker_validator import StickerValidator
from ..utils.storage import StickerStorage

class MessageSticker(models.Model, LoggableMixin):
    """
    Modelo principal para la gestión de stickers de WhatsApp.
    Implementa el patrón Repository para el acceso a datos y
    Single Responsibility Principle separando las responsabilidades.
    """
    _name = 'message_app.message_sticker'
    _description = 'Model Sticker'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']
    
    # Campos del modelo con mejor documentación y validaciones
    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        tracking=True
    )

    sticker_url = fields.Text(
        string='Sticker URL',
        required=True,
        tracking=True
    )

    file_name = fields.Char(
        string='File Name',
        required=True
    )

    mime_type = fields.Selection([
        ('image/webp', 'WebP'),
        ('image/png', 'PNG'),
        ('image/jpeg', 'JPEG')
    ], string='MIME Type', required=True, default='image/webp')

    description = fields.Text(
        string='Description',
        tracking=True
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True
    )

    _sql_constraints = [
        ('unique_file_name', 
         'UNIQUE(file_name)',
         'The file name must be unique!')
    ]

    @api.model
    def create_default_stickers_model(self):
        """
        Crea stickers predeterminados si no existen.
        Implementa el patrón Factory para la creación de stickers.
        """
        try:
            if not self._default_stickers_exist():
                default_stickers = self._get_default_sticker_data()
                return self._create_multiple_stickers(default_stickers)
            self.logger.info("Default stickers already exist.")
            return False
        except Exception as e:
            self.logger.error(f"Error creating default stickers: {str(e)}", exc_info=True)
            raise UserError("Failed to create default stickers.")

    @api.model
    def add_sticker(self, name, file_path, file_name, mime_type, description=None):
        """
        Agrega un nuevo sticker validando los datos de entrada.
        
        Args:
            name (str): Nombre del sticker
            file_path (str): Ruta del archivo
            file_name (str): Nombre del archivo
            mime_type (str): Tipo MIME del archivo
            description (str, optional): Descripción del sticker
            
        Returns:
            record: Registro del nuevo sticker creado
            
        Raises:
            UserError: Si la validación falla
        """
        validator = StickerValidator()
        storage = StickerStorage()

        try:
        # Validar datos de entrada
            validator.validate_sticker_data(name, file_path, file_name, mime_type)
            
            # Procesar y almacenar el archivo
            sticker_url = storage.store_sticker_file(file_path, file_name)
            
            # Crear el registro
            sticker = self.create({
                'name': name,
                'file_name': file_name,
                'sticker_url': sticker_url,
                'mime_type': mime_type,
                'description': description,
            })
            return sticker
        except UserError as ue:
            self.logger.warning(f"Validation failed: {str(ue)}")
            raise
        except Exception as e:
            self.logger.error(f"Error adding sticker: {str(e)}", exc_info=True)
            raise UserError(f"Sticker creation failed: {str(e)}")

    def delete_sticker(self):
        """
        Elimina un sticker de manera segura implementando soft delete.
        """
        self.ensure_one()
        try:
            if not self.active:
                raise UserError("This sticker is already deleted.")
                
            # Implementar soft delete
            self.write({'active': False})
            
            # Eliminar archivo físico si es necesario
            storage = StickerStorage()
            storage.remove_sticker_file(self.file_name)
        except UserError as ue:
            self.logger.warning(f"Delete failed: {str(ue)}")
            raise
        except Exception as e:
            self.logger.error(f"Error deleting sticker: {str(e)}", exc_info=True)
            raise UserError("Failed to delete sticker.")

    def _default_stickers_exist(self):
        """
        Verifica si ya existen stickers predeterminados.
        
        Returns:
            bool: True si existen stickers predeterminados
        """
        try:
            return bool(self.search_count([]))
        except Exception as e:
            self.logger.error(f"Error checking default stickers: {str(e)}", exc_info=True)
            return False

    def _get_default_sticker_data(self):
        """
        Obtiene la configuración de stickers predeterminados.
        
        Returns:
            list: Lista de diccionarios con datos de stickers
        """
        return [
            {
                'name': 'Baile',
                'file_name': 'baile.webp',
                'sticker_url': '/message_app/static/src/assets/img/stickers/baile.webp',
                'mime_type': 'image/webp'
            },
            {
                'name': 'Grito',
                'file_name': 'grito.webp',
                'sticker_url': '/message_app/static/src/assets/img/stickers/grito.webp',
                'mime_type': 'image/webp'
            },
            {
                'name': 'Kirbi',
                'file_name': 'kirbi.webp',
                'sticker_url': '/message_app/static/src/assets/img/stickers/kirbi.webp',
                'mime_type': 'image/webp'
            }
        ]

    @api.model
    def _create_multiple_stickers(self, stickers_data):
        """
        Crea múltiples stickers de manera eficiente.
        
        Args:
            stickers_data (list): Lista de diccionarios con datos de stickers
            
        Returns:
            recordset: Conjunto de registros creados
        """
        try:
            return self.create(stickers_data)
        except Exception as e:
            self.logger.error(f"Error creating multiple stickers: {str(e)}", exc_info=True)
            raise UserError("Failed to create multiple stickers.")