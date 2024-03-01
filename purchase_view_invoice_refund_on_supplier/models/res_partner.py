# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _purchase_invoice_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        purchase_order_groups = self.env['purchase.order'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in purchase_order_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.purchase_order_count += group['partner_id_count']
                partner = partner.parent_id

        supplier_invoice_groups = self.env['account.invoice'].read_group(
            domain=[('partner_id', 'in', all_partners.ids),
                    ('type', 'in', ('in_invoice', 'in_refund'))],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in supplier_invoice_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.supplier_invoice_count += group['partner_id_count']
                partner = partner.parent_id
