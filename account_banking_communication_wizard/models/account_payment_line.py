# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    invoice_id = fields.Many2one(
        string='Invoice',
        store=True,
        comodel_name='account.invoice',
        compute="_compute_invoice_id")

    @api.depends('move_line_id')
    def _compute_invoice_id(self):
        for record in self:
            if record.move_line_id:
                record.invoice_id = record.move_line_id.invoice_id
