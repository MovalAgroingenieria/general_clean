# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    created_by_authdnie = fields.Boolean(
        string='Created by AuthDNIe',
        default=False,
        readonly=True)
