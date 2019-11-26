# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountPaymentMode(models.Model):
    _inherit = "account.payment.mode"


    # Overwrite original field
    note = fields.Html(
        string='Note',
        translate=True)
