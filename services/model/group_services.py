from odoo.exceptions import UserError
from typing import Dict, List
from odoo.http import request
from odoo import api, SUPERUSER_ID
from ...config.api_config import APIConfig
from ...utils.log.extra_logger_config import ExtraLoggerConfig

class GroupService:
    
    def __init__(self, env):
        self.env = env
        self.api_config = APIConfig()
        self.logger = ExtraLoggerConfig().get_logger("group_services")

    def process_group_update(self, group_data: Dict) -> int:
        """
        Processes a group update from WhatsApp.
        
        Args:
            group_data (dict): Group data from WhatsApp
            
        Returns:
            int: ID of the processed group
            
        Raises:
            UserError: If processing fails
        """
        try:
            env = request.env if request else self.env  # Usa request.env si está disponible, sino usa self.env
            group_model = env['message_app.message_group']
            return group_model.create_or_update_group(group_data)
        except Exception as e:
            self.logger.error(f"Error processing group update: {str(e)}", exc_info=True)
            raise UserError("Error processing group update.")

    @api.model
    def bulk_process_groups(self, groups_data: List[Dict]) -> List[int]:
        """
        Processes multiple group updates in bulk.
        
        Args:
            groups_data (list): List of group data
            
        Returns:
            list: List of processed group IDs
        """
        processed_ids = []
        for group_data in groups_data:
            try:
                group_id = self.process_group_update(group_data)
                processed_ids.append(group_id)
            except Exception as e:
                self.logger.error(f"Error processing group: {str(e)}", exc_info=True)
                continue
        self.logger.info(f"Bulk processing completed. Processed {len(processed_ids)} groups.")
        return processed_ids

    @staticmethod
    def create_or_update_group(model, group_data):
        """Crea o actualiza un grupo de WhatsApp en la base de datos."""
        try:
            if not isinstance(group_data, dict):
                raise UserError("Group data must be a dictionary.")

            serialized_id = group_data.get('id', {}).get('_serialized')
            if not serialized_id or 'participants' not in group_data:
                raise UserError("Invalid group data format.")
            
            group = model.search([('serialized', '=', serialized_id)], limit=1)
            group_values = {
                'group_number': group_data['id'].get('user'),
                'group_name': group_data.get('subject'),
                'serialized': serialized_id,
            }

            if group:
                group.write(group_values)
            else:
                group = model.create(group_values)

            # Actualizar miembros del grupo
            participants = group_data.get('participants', [])
            if not isinstance(participants, list):
                raise UserError("Participants data must be a list.")

            model.env['message_app.message_group_member'].create_or_update_members(group.id, participants)
            
            return group.id
        except Exception as e:
            logger = ExtraLoggerConfig().get_logger("group_services")
            logger.error(f"Error in create_or_update_group: {str(e)}", exc_info=True)
            raise UserError("Error creating or updating group.")
