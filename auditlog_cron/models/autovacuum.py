# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, api


_logger = logging.getLogger(__name__)


class AuditlogAutovacuum(models.TransientModel):
    _inherit = 'auditlog.autovacuum'

    @api.model
    def autovacuum_admin(self, user_id):
        """Delete all logs owned by Admin (user_id = ``user_id``). Includes:
            - CRUD logs (create, read, write, unlink)
            - HTTP requests
            - HTTP user sessions
        Called from a cron.
        """
        table_models = (
            'auditlog_log',
            'auditlog_http_request',
            'auditlog_http_session',)
        for table_model in table_models:
            try:
                query = 'DELETE FROM ' + table_model + \
                    ' WHERE user_id = ' + str(user_id)
                self.env.cr.execute(query)
                _logger.info("AUTOVACUUM ADMIN: records of table %s deleted."
                             % table_model)
            except Exception:
                _logger.info("AUTOVACUUM ADMIN: Error deleting records of "
                             "table %s." % table_model)
