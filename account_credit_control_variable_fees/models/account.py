# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    apply_variable_fees = fields.Boolean(
        string='Apply variable fees (Credit control)',
        default=True,
        help="Uncheck this box if you do not want to apply the variable fees "
             "to the lines of this journal in Credit control.")
