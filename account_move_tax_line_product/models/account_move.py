# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, api


_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def add_product_id_to_tax_account_move_line(self):
        # Get tax account move lines
        tax_move_lines = self.env['account.move.line'].search(
            [('invoice_id', '!=', False), ('tax_line_id', '!=', False),
             ('product_id', '=', False)])
        num_tax_move_lines = len(tax_move_lines)
        _logger.info("TAX LINES WITHOUT PRODUCT: %s" % num_tax_move_lines)
        # Insert product_id in tax move line based on invoice
        if num_tax_move_lines > 0:
            for tax_move_line in tax_move_lines:
                invoice = self.env['account.invoice'].browse(
                    tax_move_line.invoice_id.id)
                for invoice_line in invoice.invoice_line_ids:
                    if (invoice_line.account_id == tax_move_line.account_id and
                        invoice_line.account_analytic_id ==
                            tax_move_line.analytic_account_id):
                        tax_move_line.product_id = invoice_line.product_id
                        _logger.info("INSERT PRODUCT %s IN TAX LINE %s."
                                     % (invoice_line.product_id.name,
                                        tax_move_line.id))
