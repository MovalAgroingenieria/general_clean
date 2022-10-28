# -*- coding: utf-8 -*-
# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    in_dipucr = fields.Boolean(
        string="In DipuCR",
        readonly=True,
        help='Indicates whether this payment has already been done and '
             'uploaded successfully')

    dipucr_ref = fields.Char(
        string="DipuCR Reference",
        readonly=True,
        help='This number indicates the payment reference when has been made '
             'by DipuCR')
