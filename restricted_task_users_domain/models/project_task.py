# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class CustomProjectTask(models.Model):
    _inherit = 'project.task'

    # Override the user_id field to change its domain
    user_id = fields.Many2one(
        'res.users',
        string='Assigned to',
        index=True,
        track_visibility='onchange',
        domain=lambda self: [('groups_id', 'not in',
                              self.env.ref('base.group_portal').id)],
    )
