# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    in_suma = fields.Boolean(
        string="In SUMA",
        readonly=True,
        help='Indicates whether this payment has already been done and '
             'uploaded successfully')

    suma_ref = fields.Char(
        string="SUMA Reference",
        readonly=True,
        help='This number indicates the payment reference when has been made '
             'by SUMA')

    suma_rejected = fields.Boolean(
        string="SUMA Rejected",
        help='Indicates that the invoice has been rejected by SUMA')

    suma_leave_requested = fields.Boolean(
        string="SUMA Leave Requested",
        help='Indicates that a SUMA leave has been requested')
