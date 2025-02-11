# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    in_n63_s1 = fields.Boolean(
        string="In n63 Stage 1",
        readonly=True,
        help='Indicates whether this payment has already been done and '
             'uploaded successfully in stage 1')

    in_n63_s3 = fields.Boolean(
        string="In n63 Stage 3",
        readonly=True,
        help='Indicates whether this payment has already been done and '
             'uploaded successfully in stage 3')

    n63_s1_ref = fields.Char(
        string="N63 Stage 1 Reference",
        readonly=True,
        help='This number indicates the payment reference when has been made '
             'by n63 in Stage 1')

    n63_s3_ref = fields.Char(
        string="N63 Stage 3 Reference",
        readonly=True,
        help='This number indicates the payment reference when has been made '
             'by N63 in Stage 3')

    n63_s1_rejected = fields.Boolean(
        string="N63 Stage 1 Rejected",
        help='Indicates that the invoice has been rejected by N63 in Stage 1')

    n63_s3_rejected = fields.Boolean(
        string="N63 Stage 3 Rejected",
        help='Indicates that the invoice has been rejected by N63 in Stage 3')
