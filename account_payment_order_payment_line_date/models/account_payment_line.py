# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    def _prepare_account_payment_vals(self):
        journal = self.order_id.journal_id
        vals = {
            "payment_type": self.order_id.payment_type,
            "partner_id": self.partner_id.id,
            "destination_account_id": self.move_line_id.account_id.id,
            "company_id": self.order_id.company_id.id,
            "amount": sum(self.mapped("amount_currency")),
            "date": self[:1].date,
            "currency_id": self.currency_id.id,
            "ref": self.order_id.name,
            "payment_reference": " - ".join(
                [line.communication for line in self]),
            "journal_id": journal.id,
            "partner_bank_id": self.partner_bank_id.id,
            "payment_order_id": self.order_id.id,
            "payment_method_id":
                self.order_id.payment_mode_id.payment_method_id.id,
            "payment_line_ids": [(6, 0, self.ids)],
        }
        # Determine partner_type
        move_type = self[:1].move_line_id.move_id.move_type
        if move_type in {"out_invoice", "out_refund"}:
            vals["partner_type"] = "customer"
        elif move_type in {"in_invoice", "in_refund"}:
            vals["partner_type"] = "supplier"
        else:
            p_type = \
                "customer" if vals["payment_type"] == "inbound" else "supplier"
            vals["partner_type"] = p_type
        if not vals["destination_account_id"]:
            if vals["partner_type"] == "customer":
                vals[
                    "destination_account_id"
                ] = self.partner_id.property_account_receivable_id.id
            else:
                vals[
                    "destination_account_id"
                ] = self.partner_id.property_account_payable_id.id
        return vals
