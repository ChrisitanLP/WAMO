from odoo import models, fields, api
import phonenumbers
from odoo.exceptions import UserError, ValidationError
from typing import List, Dict, Optional, Any
from dateutil.relativedelta import relativedelta
from datetime import datetime
from .mixins.loggable import LoggableMixin
from ..utils.response.requests import get_request
from ..services.model.user_services import UserService
from ..utils.validation.phone_validator import PhoneValidator
from ..utils.validation.serialized_validator import SerializedValidator
from ..config.api_config import APIConfig

class MessageUser(models.Model, LoggableMixin):
    """
    Modelo de usuario que administra la información del usuario y las interacciones con API externas. 
    Implementa principios de código limpio y sigue los principios SOLID.
    """
    _name = 'message_app.message_user'
    _description = 'Model User'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'message_app.loggable']
    _order = 'create_date DESC'

    # Campos con atributos adecuados para la optimización
    # region Fields
    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        index=True,
        tracking=True
    )
    display_name = fields.Char(
        string='Display Name',
        required=True,
        tracking=True
    )
    serialized = fields.Char(
        string='Serialized',
        required=True,
        index=True,
        copy=False
    )
    server = fields.Char(
        string='Server',
        required=True
    )
    active = fields.Boolean(
        default=True,
        tracking=True
    )
    last_sync = fields.Datetime(
        string='Last Synchronization',
        readonly=True
    )

    # Relaciones con atributos adecuados
    chats = fields.One2many(
        'message_app.message_chat',
        'user_id',
        string='Chats',
        copy=False
    )

    contacts = fields.One2many(
        'message_app.message_contact',
        'user_id',
        string='Contacts',
        copy=False
    )

    connection_id = fields.Many2one(
        'message_app.message_connection',
        string='Connection',
        ondelete='cascade',
        index=True
    )
    # endregion

    # region SQL Constraints
    _sql_constraints = [
        ('unique_serialized',
         'unique(serialized)',
         'The serialized value must be unique.')
    ]
    # endregion

    @property
    def api_client(self):
        if not self._api_client:
            self._api_client = APIConfig()
        return self._api_client

    @api.constrains('serialized')
    def _check_serialized_validity(self):
        for record in self:
            if not SerializedValidator.is_valid_serialized(record.serialized):
                raise UserError("Invalid serialized format. It must be a valid phone number followed by @c.us.")

    # Validation Methods
    @api.constrains('phone_number')
    def _check_phone_number(self):
        """Validates phone number format"""
        for record in self:
            try:
                parsed_number = PhoneValidator.parse(record.phone_number, None)
                if not PhoneValidator.is_valid_number(parsed_number):
                    raise ValidationError(f"Invalid phone number: {record.phone_number}")
            except phonenumbers.NumberParseException:
                raise ValidationError(f"Could not parse phone number: {record.phone_number}")

    # region Initial Load
    @api.model
    def initial_load(self) -> None:
        """
        Carga inicial de información de usuario desde la API. 
        Implementa el manejo y registro de errores.
        """
        try:
            user_service = UserService()
            account_info_list = user_service.get_account_info()

            if not account_info_list:
                raise UserError("No se recuperó información de cuenta de la API.")

            self._process_account_info(account_info_list)
            self._log_sync_success(len(account_info_list))

        except Exception as e:
            self.logger.error("Carga inicial fallida: %s", str(e), exc_info=True)
            raise UserError(f"Carga inicial fallida: {str(e)}") from e
    # endregion

    def _process_account_info(self, account_info_list: List[Dict]) -> None:
        """
        Procesar información de la cuenta y crear/actualizar usuarios.
        Args:
        account_info_list: Lista de diccionarios de información de la cuenta
        """
        for account_info in account_info_list:
            self._create_or_update_user(account_info)

    # region Create or Update User
    def _create_or_update_user(self, user_data) -> None:
        """
        Crea o actualiza un registro de usuario y lo asocias con la conexión.
        Args:
        user_data: Diccionario que contiene información del usuario
        """
        try:
            connection_id = self._find_connection_id(user_data.get('phone_number'))
            user_values = self._prepare_user_values(user_data, connection_id)
            
            if not PhoneValidator.is_valid_phone(user_values['phone_number']):
                raise UserError("Invalid phone number format. It should be in the format +<country_code><number>.")
            if not SerializedValidator.is_valid_serialized(user_values['serialized']):
                raise UserError("Invalid serialized format. It should be in the format <country_code><number>@c.us")

            existing_user = self._find_existing_user(user_data.get('serialized'))
            if existing_user:
                existing_user.write(user_values)
            else:
                self.create(user_values)

        except Exception as e:
            self.logger.error("Error al crear/actualizar usuario: %s", str(e), exc_info=True)
            raise UserError(f"Error al crear/actualizar usuario: {str(e)}") from e
    #endregion

    def _find_connection_id(self, phone_number: str) -> Optional[int]:
        """
        Buscar ID de conexión por número de teléfono.
        Argumentos:
        phone_number: Número de teléfono que se buscará
        Devuelve:
        Opcional[int]: ID de conexión si se encuentra, Falso en caso contrario
        """
        connection = self.env['message_app.message_connection'].search([
            ('phone_number', '=', phone_number)
        ], limit=1)
        return connection.id if connection else False

    def _find_existing_user(self, serialized: str) -> Optional['MessageUser']:
        """
        Busque un usuario existente por valor serializado.
        Argumentos:
        serializado: valor serializado que se buscará
        Devuelve:
        Opcional[MessageUser]: registro de usuario existente si se encuentra
        """
        return self.search([('serialized', '=', serialized)], limit=1)

    def _prepare_user_values(self, user_data: Dict[str, Any], connection_id: Optional[int]) -> Dict[str, Any]:
        """
        Preparar valores para la creación/actualización de usuarios.
        Args:
        user_data: Diccionario que contiene información del usuario
        connection_id: ID de conexión opcional
        Retornos:
        Dict[str, Any]: Valores preparados para el registro del usuario
        """
        return {
            'phone_number': user_data.get('phone_number'),
            'display_name': user_data.get('display_name'),
            'serialized': user_data.get('serialized'),
            'server': user_data.get('server'),
            'connection_id': connection_id,
            'last_sync': datetime.now(),
        }

    def _log_sync_success(self, count: int) -> None:
        """
        Registrar sincronización exitosa.
        Argumentos:
        count: Número de cuentas procesadas
        """
        self.logger.info("Sincronizado exitosamente %s accounts", count)
        self.write({'last_sync': fields.Datetime.now()})

    @api.model
    def cleanup_inactive_users(self, days: int = 90) -> None:
        """
        Limpiar usuarios inactivos con más de los días especificados.
        Args:
        días: Número de días de inactividad antes de la limpieza
        """
        cutoff_date = fields.Datetime.now() - relativedelta(days=days)
        inactive_users = self.search([
            ('last_sync', '<', cutoff_date),
            ('active', '=', True)
        ])
        
        if inactive_users:
            inactive_users.write({'active': False})
            self.logger.info("Deactivated %s inactive users", len(inactive_users))