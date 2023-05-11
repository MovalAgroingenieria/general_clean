# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    def draft2open_payment_line_check(self):
        res = super().draft2open_payment_line_check()
        sepa_dd_lines = self.filtered(
            lambda l: l.order_id.payment_method_id.code == "csb_direct_debit")
        sepa_dd_lines._check_sepa_direct_debit_ready()
        return res
