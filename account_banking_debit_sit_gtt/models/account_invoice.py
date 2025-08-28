# -*- coding: utf-8 -*-
# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    in_sit_gtt = fields.Boolean(
        string="In SIT GTT",
        readonly=True,
        help="Indicates whether this payment has already been done and "
             "uploaded successfully")

    sit_gtt_ref = fields.Char(
        string="SIT GTT Reference",
        readonly=True,
        help="This number indicates the payment reference when has been made "
             "by SIT GTT")
