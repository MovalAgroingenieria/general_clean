# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
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
                    record.payment_mode_id.payment_method_id and
                    'sepa' in record.payment_mode_id.payment_method_id.code):
                is_sepa_mismatch = True
            record.is_sepa_mismatch = is_sepa_mismatch

    @api.multi
    def generated2uploaded(self):
        eur = self.env.ref('base.EUR')
        for order in self:
            if order.is_sepa_mismatch:
                errors = []
                if order.company_partner_bank_id.acc_type != 'iban':
                    errors.append(_(
                        'Company bank account is not set as IBAN.'))
                for pline in order.payment_line_ids:
                    if pline.currency_id != eur:
                        errors.append(
                            _('Payment line with reference %s has a currency '
                              'that is not EUR.') % (pline.name or 'unknown'),
                        )
                    if pline.partner_bank_id.acc_type != 'iban':
                        errors.append(
                            _('Payment line with reference %s has a bank '
                              'account that is not set as IBAN.') % (
                                pline.name or 'unknown'),
                        )
                raise ValidationError(
                    _('The following errors were found:\n') + '\n'.join(
                        errors),
                )
        res = super(AccountPaymentOrder, self).generated2uploaded()
        return res
