# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    _logger = logging.getLogger(__name__)
    _logger.info('Adding company_id to existing records')
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('Get company id')
    company = env['res.company'].search([], order='id', limit=1)
    _logger.info('Add company_id to registres')
    env.cr.execute("""
        UPDATE res_letter SET company_id = %s WHERE company_id IS NULL;
        """, (company.id,))
    env.cr.commit()
    env.invalidate_all()
    _logger.info('Post-init hook completed')
