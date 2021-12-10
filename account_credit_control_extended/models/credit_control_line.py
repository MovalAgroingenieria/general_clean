# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class CreditControlLine(models.Model):
    _inherit = "credit.control.line"

    invoice_date = fields.Date(
        string="Invoice date",
        compute="_compute_invoice_date")

    @api.multi
    def _compute_invoice_date(self):
        for record in self:
            if record.invoice_id:
                record.invoice_date = record.invoice_id.date
