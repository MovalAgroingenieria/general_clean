# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountAnalyticDistribution(models.Model):
    _inherit = "account.analytic.distribution"

    active = fields.Boolean(
        default=True)
