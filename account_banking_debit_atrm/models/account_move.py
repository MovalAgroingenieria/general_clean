# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def _check_lock_date(self):
        check_lock_date = True
        try:
            payment_order_id = self.line_ids[0].payment_line_ids[
                0].bank_line_id[0].order_id[0].id
            payment_order = self.env['account.payment.order'].browse(
                payment_order_id)
            if payment_order.payment_mode_name == u'ATRM':
                check_lock_date = payment_order.check_lock_date
            else:
                super(AccountMove, self)._check_lock_date()
        except Exception:
            super(AccountMove, self)._check_lock_date()
        if check_lock_date:
            for move in self:
                lock_date = max(move.company_id.period_lock_date,
                                move.company_id.fiscalyear_lock_date)
                if self.user_has_groups('account.group_account_manager'):
                    lock_date = move.company_id.fiscalyear_lock_date
                if move.date <= lock_date:
                    if self.user_has_groups('account.group_account_manager'):
                        message = _("You cannot add/modify entries prior to "
                                    "and inclusive of the lock date %s") % \
                            (lock_date)
                    else:
                        message = _("You cannot add/modify entries prior to "
                                    "and inclusive of the lock date %s. Check "
                                    "the company settings or ask someone with "
                                    "the 'Adviser' role") % (lock_date)
                    raise UserError(message)
        return True
