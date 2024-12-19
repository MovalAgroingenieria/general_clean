# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class OmaToken(models.Model):
    _name = 'oma.token'
    _description = 'Mobile Device Token'

    name = fields.Char(
        string='Token Name',
        required=True,
    )
    device_type = fields.Selection(
        selection=[
            ('01_android', 'Android'),
            ('02_ios', 'iOS'),
            ('99_unknown', 'Unknown'),
        ],
        string='Device Type',
        required=True,
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The token name must be unique.'),
    ]
