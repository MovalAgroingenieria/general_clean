# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def onchange_partner(self):
        values = {
            'pricelist_id': self.partner_id.product_pricelist_id and
            self.partner_id.product_pricelist_id.id or False,
        }
        self.update(values)

    @api.model
    def create(self, vals):
        # Makes sure 'pricelist_id' are defined
        if any(f not in vals for f in ['pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['pricelist_id'] = vals.setdefault(
                'pricelist_id', partner.product_pricelist_id and
                partner.product_pricelist_id.id)
        result = super(purchase_order, self).create(vals)
        return result
