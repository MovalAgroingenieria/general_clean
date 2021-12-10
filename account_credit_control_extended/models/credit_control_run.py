# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CreditControlRun(models.Model):
    _inherit = "credit.control.run"

    run_description = fields.Text(
        string="Description")
