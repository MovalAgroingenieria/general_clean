# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    restricted_user_ids = fields.Many2many(
        string='Restricted Users',
        comodel_name='res.users',
        relation='project_task_restricted_user_ids_rel',
        column1='task_id',
        column2='user_id',
    )

    @api.model
    def create(self, vals):
        project = self.env['project.project'].browse(vals.get('project_id'))
        if 'restricted_user_ids' not in vals:
            vals['restricted_user_ids'] = [
                (6, 0, project.restricted_user_ids.ids)]
        return super(ProjectTask, self).create(vals)
