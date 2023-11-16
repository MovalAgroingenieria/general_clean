# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger = logging.getLogger(__name__)
    _logger.info(
        'Migration 10.0.1.1.2: Delete portal group from internal users')
    delete_portal_group_from_internal_users(env, version)


def delete_portal_group_from_internal_users(env, version):
    # Delete implied_ids
    user_group_lettermgmt = env.ref(
        'crm_lettermgmt.group_crm_lettermgmt_user')
    user_group_lettermgmt.implied_ids = [(6, 0, [])]
    # Unlink portal users
    portal_group = env.ref('base.group_portal')
    user_group_id = env.ref('base.group_user').id
    intern_users = env['res.users'].search(
        [('groups_id', '=', user_group_id)])
    for intern_user in intern_users:
        portal_group.users = [(3, intern_user.id)]
