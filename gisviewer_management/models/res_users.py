# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    gisviewer_profile_id = fields.Many2one(
        string='GIS Profile',
        comodel_name='gisviewer.profile',
        ondelete='restrict',
    )
