# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    message_follower_ids = fields.One2many(
        groups='base.group_user, '
               'project_limited_access.group_portal_project_user',
    )
