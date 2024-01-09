# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    values = env['ir.values'].sudo()
    # Initialize the "sequence_complaint_code_id" param (Many2one).
    try:
        sequence_coding_code_id = env.ref(
            'cim_complaints_channel.sequence_complaint_code').id
    except (Exception, ):
        sequence_coding_code_id = 0
    if sequence_coding_code_id > 0:
        values.set_default('res.cim.config.settings',
                           'sequence_complaint_code_id',
                           sequence_coding_code_id)
    # Initialize the rest of the params.
    values.set_default('res.cim.config.settings',
                       'length_tracking_code', 8)
    values.set_default('res.cim.config.settings',
                       'automatic_email_state', False)
    values.set_default('res.cim.config.settings',
                       'automatic_email_validate_com', False)
    values.set_default('res.cim.config.settings',
                       'notice_period', 15)
    values.set_default('res.cim.config.settings',
                       'deadline', 3)
    values.set_default('res.cim.config.settings',
                       'deadline_extended', 6)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env.cr.savepoint()
        env.cr.execute("""
            DELETE FROM ir_values
            WHERE model='res.cim.config.settings'""")
        env.cr.commit()
    except (Exception,):
        env.cr.rollback()
