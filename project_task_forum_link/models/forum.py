# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class Forum(models.Model):

    _inherit = 'forum.forum'

    visible_from_tasks = fields.Boolean(
        string='Visible from tasks',
        default=False,
    )

    default_user_from_tasks = fields.Many2one(
        string='Default User that create from tasks',
        comodel_name='res.users',
        ondelete='restrict',
    )


class Post(models.Model):

    _inherit = 'forum.post'

    task_id = fields.Many2one(
        string='Origin Task',
        comodel_name='project.task',
        ondelete='restrict',
    )
