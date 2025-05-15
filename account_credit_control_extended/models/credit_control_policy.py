# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class CreditControlPolicy(models.Model):
    _inherit = "credit.control.policy"

    limit_date = fields.Date(
        string="Limit date",
    )

    @api.multi
    def _move_lines_domain(self, controlling_date):
        domain = super(CreditControlPolicy, self)._move_lines_domain(
            controlling_date)
        if self.limit_date:
            domain += [('date_maturity', '>=', self.limit_date)]
        return domain
