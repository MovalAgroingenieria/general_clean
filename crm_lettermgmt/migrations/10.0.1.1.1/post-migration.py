# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger = logging.getLogger(__name__)
    _logger.info('Migration 10.0.1.1.1: Assign portal group to portal users')
    assing_portal_group_to_portal_users(env, version)
    _logger.info('Migration 10.0.1.1.1: Assign user group to internal users')
    assing_user_group_to_users(env, version)
    _logger.info('Migration 10.0.1.1.1: Delete old config parameter')
    delete_ir_config_parameter(env, version)


def assing_portal_group_to_portal_users(env, version):
    ir_config_parameter = env['ir.values'].search(
        [('name', '=', 'enable_access_res_letter_portal_user')])
    # Assign to portal user except if original config params is set to False
    if ir_config_parameter.value != 'I00\n.':
        portal_group_id = env.ref('base.group_portal').id
        portal_group_lettermgmt = env.ref(
            'crm_lettermgmt.group_crm_lettermgmt_portal')
        portal_users = env['res.users'].search(
            [('groups_id', '=', portal_group_id)])
        portal_group_lettermgmt.users = \
            [(4, portal_user.id) for portal_user in portal_users]


def assing_user_group_to_users(env, version):
    user_group_id = env.ref('base.group_user').id
    user_group_lettermgmt = env.ref(
        'crm_lettermgmt.group_crm_lettermgmt_user')
    intern_users = env['res.users'].search(
        [('groups_id', '=', user_group_id)])
    user_group_lettermgmt.users = \
        [(4, intern_user.id) for intern_user in intern_users]


def delete_ir_config_parameter(env, version):
    ir_config_parameter = env['ir.values'].search(
        [('name', '=', 'enable_access_res_letter_portal_user')])
    if ir_config_parameter:
        ir_config_parameter.unlink()
