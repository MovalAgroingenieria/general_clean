# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger = logging.getLogger(__name__)
    _logger.info(
        'Migration 10.0.1.1.4: Assing lettermgmt portal group to portal users')
    assing_portal_group_to_portal_users(env, version)


def assing_portal_group_to_portal_users(env, version):
    portal_group_id = env.ref('base.group_portal').id
    portal_group_lettermgmt = env.ref(
        'crm_lettermgmt.group_crm_lettermgmt_portal')
    portal_users = env['res.users'].search(
        [('groups_id', '=', portal_group_id)])
    portal_group_lettermgmt.users = \
        [(4, portal_user.id) for portal_user in portal_users]
