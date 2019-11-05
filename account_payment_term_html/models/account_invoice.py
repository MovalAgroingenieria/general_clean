# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"


    # Overwrite original field
    note = fields.Html(
        string='Description on the Invoice',
        translate=True)
