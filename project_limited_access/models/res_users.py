# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class Users(models.Model):

    _inherit = 'res.users'

    @api.model
    def action_get(self):
        if self.env.user.has_group(
                'project_limited_access.group_portal_project_user'):
            return self.sudo().env.ref('base.action_res_users_my').read()[0]
        else:
            return super(Users, self).action_get()

    @api.depends('groups_id')
    def _compute_share(self):
        user_group_id = self.env['ir.model.data'].xmlid_to_res_id(
            'base.group_user')
        project_group_id = self.env['ir.model.data'].xmlid_to_res_id(
            'project_limited_access.group_portal_project_user')
        internal_users = self.filtered_domain(
            [('groups_id', 'in', [user_group_id, project_group_id])])
        internal_users.share = False
        (self - internal_users).share = True
