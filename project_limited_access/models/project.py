# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class Project(models.Model):
    _inherit = 'project.project'

    restricted_user_ids = fields.Many2many(
        string='Restricted Users',
        comodel_name='res.users',
        help='Users who have limited access to this project and its tasks.',
        domain=lambda self: [
            ('groups_id', 'in', self.env.ref(
                'project_limited_access.group_portal_project_user').id)],
    )

    def write(self, vals):
        result = super(Project, self).write(vals)
        if 'restricted_user_ids' in vals:
            for project in self:
                project.task_ids.write(
                    {'restricted_user_ids': vals['restricted_user_ids']})
        return result
