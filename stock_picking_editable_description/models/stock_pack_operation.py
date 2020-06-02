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
        for pack_operation in self:
            if pack_operation.picking_id.picking_type_code == 'outgoing':
                for record in self:
                    # By default fill with product name
                    name_from_sale_order_line = record.product_id.name
                    found_saleorders = self.env['sale.order'].search(
                        [('procurement_group_id', '=',
                          record.picking_id.group_id.id)])
                    siz = len(found_saleorders)
                    if siz == 1:
                        saleorder = found_saleorders[0]
                        for line in saleorder.order_line:
                            if line.product_id == record.product_id:
                                name_from_sale_order_line = line.name
                                break
                    else:  # Not sale order
                        for line in record.picking_id.move_lines:
                            if line.product_id == record.product_id:
                                name_from_sale_order_line = line.name
                            else:
                                name_from_sale_order_line = \
                                    record.product_id.name
                    record.name_from_sale_order_line = \
                        name_from_sale_order_line
            else:
                for record in self:
                    for line in record.picking_id.move_lines:
                        if line.product_id == record.product_id:
                            record.name_from_sale_order_line = line.name
                        else:
                            record.name_from_sale_order_line = \
                                record.product_id.name
