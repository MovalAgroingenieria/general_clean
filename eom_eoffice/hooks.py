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
            'eom_eoffice.sequence_electronicfile_code').id
    except (Exception, ):
        sequence_coding_code_id = 0
    if sequence_coding_code_id > 0:
        values.set_default('res.eom.config.settings',
                           'sequence_electronicfile_code_id',
                           sequence_coding_code_id)
