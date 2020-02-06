# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    in_atrm = fields.Boolean(
        string="In ATRM",
        readonly=True,
        help='Indicates whether this payment has already been done and '
             'uploaded successfully')

    atrm_ref = fields.Char(
        string="ATRM Reference",
        readonly=True,
        help='This number indicates the payment reference when has been made '
             'by ATRM')

    atrm_rejected = fields.Boolean(
        string="ATRM Rejected",
        help='Indicates that the invoice has been rejected by ATRM')

    atrm_leave_requested = fields.Boolean(
        string="ATRM Leave Requested",
        help='Indicates that a ATRM leave has been requested')
