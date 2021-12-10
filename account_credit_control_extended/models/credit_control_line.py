# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreditControlLine(models.Model):
    _inherit = "credit.control.line"

    invoice_id = fields.Many2one('account.invoice',
                                 string='Invoice',
                                 readonly=True)
    invoice_number = fields.Char(
        string="Invoice number",
        compute="_compute_invoice_number")

    @api.multi
    def _compute_invoice_number(self):
        for record in self:
            if record.invoice_id:
                record.invoice_number = record.invoice_id.number
