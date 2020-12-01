# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger = logging.getLogger(__name__)
    migration_ok = change_wausms_sms_id_to_name(env)
    message = 'OK'
    if not migration_ok:
        message = 'ERROR'
    _logger.info('wausms_client, migration to version 10.0.1.1.1 ' + message)


def change_wausms_sms_id_to_name(env):
    resp = True
    try:
        env.cr.savepoint()
        env.cr.execute(
            """UPDATE wausms_tracking SET name = wausms_sms_id;
               ALTER TABLE wausms_tracking DROP COLUMN wausms_sms_id;
               UPDATE ir_values SET model = 'wausms.configuration'
                              WHERE model = 'wau.sms.configuration';""")
        env.cr.commit()
    except:
        resp = False
        env.cr.rollback()
    return resp
