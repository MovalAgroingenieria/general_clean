# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    values = env['ir.values'].sudo()
    # Initialize the "sequence_notificationset_code_id" param (Many2one)
    sequence_notificationset_code_id = 0
    try:
        sequence_notificationset_code_id = env.ref(
            'ncm_notifmgmt.sequence_notificationset_code').id
    except Exception:
        sequence_notificationset_code_id = 0
    if sequence_notificationset_code_id > 0:
        values.set_default('res.notif.config.settings',
                           'sequence_notificationset_code_id',
                           sequence_notificationset_code_id)
    # Initialize the "default_notificationset_type_id" param (Many2one)
    default_notificationset_type_id = 0
    try:
        default_notificationset_type_id = env.ref(
            'ncm_notifmgmt.notificationset_type_customers').id
    except Exception:
        default_notificationset_type_id = 0
    if default_notificationset_type_id > 0:
        values.set_default('res.notif.config.settings',
                           'default_notificationset_type_id',
                           default_notificationset_type_id)
    # Assignement of "group_ncm_user" group to all internal users.
    group_ncm_user = env.ref('ncm_notifmgmt.group_ncm_user')
    users = env['res.users'].search([])
    for user in (users or []):
        if user.has_group('base.group_user'):
            user.write({'groups_id': [(4, group_ncm_user.id)]})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env.cr.savepoint()
        env.cr.execute("""
            DELETE FROM ir_values
            WHERE model='res.notif.config.settings'""")
        env.cr.commit()
    except Exception:
        env.cr.rollback()
