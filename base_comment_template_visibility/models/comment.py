# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class BaseCommentTemplate(models.Model):
    _inherit = "base.comment.template"
    _description = "Base comment template visibility"

    active = fields.Boolean(
        string="Active",
        default=True,
        help='If the active field is set to False, it will allow you to ' +
        'hide the register without removing it. For see archived register, ' +
        'go to "Search-Filters" in tree view'
    )
