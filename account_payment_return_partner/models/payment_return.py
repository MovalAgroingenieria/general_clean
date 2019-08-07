# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class PaymentReturnLine(models.Model):
    _inherit = "payment.return.line"

    # Overwrite original field to remove domain
    expense_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Expense partner")

class AccountJournal(models.Model):
    _inherit = "account.journal"

    # Overwrite original field to remove domain
    default_expense_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Default Expense Partner",
        help='Default partner for commission expenses')
