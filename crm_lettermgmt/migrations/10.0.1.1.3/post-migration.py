# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger = logging.getLogger(__name__)
    _logger.info(
        'Migration 10.0.1.1.3: Delete portal group from partner view')
    delete_portal_group_from_partner_view(env, version)


def delete_portal_group_from_partner_view(env, version):
    # Get group and view refs
    lettermgmt_group_portal_ref = env.ref(
        'crm_lettermgmt.group_crm_lettermgmt_portal')
    res_partner_view_ref = env.ref(
        'crm_lettermgmt.view_partner_form')
    # Unlink
    res_partner_view_ref.groups_id = [(3, lettermgmt_group_portal_ref.id)]
    env.cr.commit()
