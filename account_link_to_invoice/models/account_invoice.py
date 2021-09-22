# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    linked_invoice_id = fields.Many2one(
        string='Linked Invoice',
        comodel_name='account.invoice',
        domain=[('state', 'not in', ['cancel', 'draft'])],
        ondelete='set null')

    @api.onchange('linked_invoice_id')
    def _onchange_linked_invoice_id(self):
        if self.linked_invoice_id and self.linked_invoice_id.number:
            self.origin = self.linked_invoice_id.number
        else:
            self.origin = ''
