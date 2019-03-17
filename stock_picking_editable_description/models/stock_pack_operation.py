# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


# Create calculated field to get sale.order.line.name
class PackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    name_from_sale_order_line = fields.Text(
        string='Description',
        store=True,
        compute='_compute_name_from_sale_order_line')

    @api.depends('product_id')
    def _compute_name_from_sale_order_line(self):
        for record in self:
            name_from_sale_order_line = ''
            found_saleorders = self.env['sale.order'].search(
                [('name', '=', record.picking_id.origin)])
            siz = len(found_saleorders)
            if siz == 1:
                saleorder = found_saleorders[0]
                for line in saleorder.order_line:
                    if line.product_id == record.product_id:
                        name_from_sale_order_line = line.name
                        break
            record.name_from_sale_order_line = name_from_sale_order_line
