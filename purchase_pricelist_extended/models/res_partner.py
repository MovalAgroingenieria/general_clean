# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    product_pricelist_id = fields.Many2one(
        string='Supplier Pricelist',
        comodel_name='product.pricelist',
        ondelete='restrict',
    )
