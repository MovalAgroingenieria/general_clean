# -*- coding: utf-8 -*-
# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY = 36

logger = logging.getLogger(__name__)


class AccountBankingMandate(models.Model):
    _inherit = 'account.banking.mandate'

    @api.model
    def _sdd_mandate_set_state_to_expired(self):
        expire_limit_date = datetime.today() + \
            relativedelta(months=-NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY)
        expire_limit_date_str = expire_limit_date.strftime('%Y-%m-%d')
        expired_mandates = self.env['account.banking.mandate'].search(
            ['|',
                ('last_debit_date', '=', False),
                ('last_debit_date', '<=', expire_limit_date_str),
                ('state', '=', 'valid'),
                ('signature_date', '<=', expire_limit_date_str)])
        for posible_expire_mandate in expired_mandates:
            if (posible_expire_mandate.payment_line_ids and
                    len(posible_expire_mandate.payment_line_ids) > 0):
                ordered_payment_lines = \
                    posible_expire_mandate.payment_line_ids.sorted(
                        lambda x: x.date, reverse=True)
                if (posible_expire_mandate.last_debit_date !=
                        ordered_payment_lines[0].date):
                    posible_expire_mandate.last_debit_date = \
                        ordered_payment_lines[0].date
        return super(
            AccountBankingMandate, self)._sdd_mandate_set_state_to_expired()
