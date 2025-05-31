import requests
import json
from odoo import http
from odoo.http import request, Response
import os
import stat
from odoo.exceptions import UserError
from werkzeug.utils import secure_filename
from typing import List, Dict, Any
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class FileService:
    """
    Servicio para la gestión de archivos de stickers.
    Implementa operaciones de archivo y manejo de permisos.
    """
    
    STICKERS_DIRECTORY = 'sources/custom/message_app/static/src/assets/img/stickers'

    def __init__(self):
        self.base_path = 'sources/custom/message_app/static/src/assets/media/files'
        self.chunk_size = 8192  # 8KB chunks
        self._ensure_directory()
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("sticker_storage")

    def save_sticker_file(self, file, file_name) -> str:
        """
        Guarda un archivo de sticker.
        Args:
            file: Objeto archivo
            file_name (str): Nombre del archivo
        Returns:
            str: Ruta del archivo guardado
        Raises:
            ValueError: Si no se proporciona archivo
            UserError: Si hay error al guardar
        """
        if not file:
            self.logger.warning("Intento de guardar un archivo vacío.")
            raise ValueError("No se proporcionó archivo")

        file_path = os.path.join(self.STICKERS_DIRECTORY, file_name)
        self._ensure_directory_permissions()

        try:
            with open(file_path, 'wb') as dest_file:
                self._write_file_chunks(file, dest_file)
            self.logger.info("Archivo guardado: %s", file_name)
            return file_path
        except Exception as e:
            self.logger.error(f"Error al guardar archivo {file_name}: {str(e)}", exc_info=True)
            raise UserError(f"Error al guardar el archivo: {str(e)}")

    def _ensure_directory_permissions(self) -> None:
        """Asegura que el directorio tenga los permisos correctos."""
        try:
            if not os.path.exists(self.STICKERS_DIRECTORY):
                os.makedirs(self.STICKERS_DIRECTORY, mode=0o755)
            else:
                current_permissions = stat.S_IMODE(os.lstat(self.STICKERS_DIRECTORY).st_mode)
                required_permissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO
                if current_permissions != required_permissions:
                    os.chmod(self.STICKERS_DIRECTORY, required_permissions)
                    self.logger.info("Permisos del directorio ajustados: %s", oct(required_permissions))
        except Exception as e:
            self.logger.error(f"Error al asegurar permisos del directorio: {str(e)}", exc_info=True)
            raise UserError("No se pudieron ajustar los permisos del directorio.")

    def _write_file_chunks(self, source_file, dest_file) -> None:
        """
        Escribe un archivo en chunks para optimizar memoria.
        Args:
            source_file: Archivo fuente
            dest_file: Archivo destino
        """
        try:
            while True:
                chunk = source_file.stream.read(self.chunk_size)
                if not chunk:
                    break
                dest_file.write(chunk)
        except Exception as e:
            self.logger.error(f"Error al escribir chunks de archivo: {str(e)}", exc_info=True)
            raise UserError("No se pudo escribir el archivo correctamente.")

    def save_file(self, file_data, filename) -> str:
        """Guarda un archivo de forma segura"""
        try:
            secure_name = secure_filename(filename)
            file_path = os.path.join(self.base_path, secure_name)
            
            with open(file_path, 'wb') as dest_file:
                while True:
                    chunk = file_data.stream.read(self.chunk_size)
                    if not chunk:
                        break
                    dest_file.write(chunk)
            
            self.logger.info(f"File saved successfully: {secure_name}")
            return f'/message_app/static/src/assets/media/files/{secure_name}'
        except Exception as e:
            self.logger.error(f"Error saving file: {str(e)}")
            raise

    def _ensure_directory(self) -> None:
        """Asegura que el directorio exista con los permisos correctos"""
        try:
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path, mode=0o755)
            else:
                current_perms = stat.S_IMODE(os.lstat(self.base_path).st_mode)
                required_perms = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH
                if current_perms != required_perms:
                    os.chmod(self.base_path, required_perms)
        except Exception as e:
            self.logger.error(f"Error ensuring directory: {str(e)}")
            raise
    
    def _get_chat_by_id(self, chat_id):
        """Obtiene un chat por su ID."""
        chat = request.env['whatsapp_message_api.whatsapp_chat'].search([('id', '=', chat_id)], limit=1)
        if not chat:
            return None
        return chat
        
    def _get_chat_info(self, chat):
        """Extrae la información necesaria del chat."""
        return {
            'is_group': chat.is_group,
            'phone_number': chat.phone_number,
            'client_id': chat.user_id.connection_id.phone_number
        }
        
    def _make_api_request(self, endpoint, data):
        """
        Realiza una solicitud a la API externa.
        
        Args:
            endpoint (str): Endpoint de la API
            data (dict): Datos a enviar
            
        Returns:
            dict: Respuesta formateada
        """
        try:
            api_base_url = self.api_config.get_api_url()
            api_url = f"{api_base_url}/{endpoint}"
            
            self.logger.info(f"Enviando solicitud a {api_url} con datos: {data}")
            
            response = requests.post(api_url, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.info(f"Respuesta de la API: {response_data}")
            
            if response_data.get('success'):
                return {
                    'status': 'success',
                    'message': 'Archivo enviado correctamente.',
                    'data': response_data.get('data', {})
                }
            else:
                return {
                    'status': 'error',
                    'message': response_data.get('message', 'Error desconocido en la API externa.')
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error de conexión con la API: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error de conexión con la API: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Error al procesar la solicitud: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error al procesar la solicitud: {str(e)}"
            }
            
    def send_file_by_path(self, file_name, file_content, chat_id, message_body=""):
        """
        Envía un archivo a través de WhatsApp usando una ruta de archivo.
        
        Args:
            file_name (str): Nombre del archivo
            file_content (str): Contenido del archivo (codificado)
            chat_id (int): ID del chat
            message_body (str): Texto del mensaje
            
        Returns:
            dict: Resultado de la operación
        """
        chat = self._get_chat_by_id(chat_id)
        if not chat:
            return {'status': 'error', 'message': 'Chat no encontrado.'}
            
        chat_info = self._get_chat_info(chat)
        
        data = {
            'clientId': chat_info['client_id'],
            'message': message_body,
            'fileName': file_name,
            'fileContent': file_content,
            'chatId': chat_info['phone_number'],
            'isGroup': chat_info['is_group']
        }
        
        return self._make_api_request('sendMessageOrFile2', data)
        
    def send_message_with_file(self, chat_id, uploaded_file, message_body):
        """
        Envía un mensaje con un archivo adjunto.
        
        Args:
            chat_id (int): ID del chat
            uploaded_file (FileStorage): Archivo subido
            message_body (str): Texto del mensaje
            
        Returns:
            dict: Resultado de la operación
        """
        chat = self._get_chat_by_id(chat_id)
        if not chat:
            return {'status': 'error', 'message': 'Chat no encontrado.'}
            
        phone_number = chat.phone_number
        
        data = {
            'tel': phone_number,
            'archivo': uploaded_file,
            'mensaje': message_body
        }
        
        return self._make_api_request('sendMessageFiles', data)