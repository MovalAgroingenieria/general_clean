# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    in_external_collector = fields.Boolean(
        string="In collection",
        readonly=True,
        help='Indicates whether this payment has already been done and '
             'uploaded successfully to external collector.')

    external_collector_ref = fields.Char(
        string="External Collector Ref.",
        readonly=True,
        help='This number indicates the payment reference when has been sent '
             'to External Collector')
