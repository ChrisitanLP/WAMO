from odoo import models
from ...utils.log.logger_config import LoggerConfig

class LoggableMixin(models.AbstractModel):
    _name = 'message_app.loggable'
    _description = 'Logging Mixin'

    @property
    def logger(self):
        if not hasattr(self.env, '_message_app_loggers'):
            self.env._message_app_loggers = {}

        if self._name not in self.env._message_app_loggers:
            logger_config = LoggerConfig(self.env)
            self.env._message_app_loggers[self._name] = logger_config.get_logger(self._name)

        return self.env._message_app_loggers[self._name]
