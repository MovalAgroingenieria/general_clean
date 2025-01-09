# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    is_sepa_mismatch = fields.Boolean(
        string='SEPA Mismatch',
        help='Indicates that the payment order has a SEPA mismatch',
        compute='_compute_is_sepa_mismatch',
    )

    @api.multi
    @api.depends('sepa', 'payment_mode_id')
    def _compute_is_sepa_mismatch(self):
        for record in self:
            is_sepa_mismatch = False
            if (not record.sepa and record.payment_mode_id and
                    record.payment_mode_id.paymet_method_id.code
                    .contains('sepa')):
                is_sepa_mismatch = True
            record.is_sepa_mismatch = is_sepa_mismatch

    @api.multi
    def generated2uploaded(self):
        res = super(AccountPaymentOrder, self).generated2uploaded()
        for order in self:
            if order.payment_mode_id.name == 'SUMA':
                for bline in order.bank_line_ids:
                    if bline.suma_sent:
                        for l in bline.payment_line_ids:
                            if bline.name == l.bank_line_id.name:
                                invoice = l.invoice_id
                                invoice.write({
                                    'in_suma': True,
                                    'suma_ref': bline.suma_ref,
                                })
        return res
