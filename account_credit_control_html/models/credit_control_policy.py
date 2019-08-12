# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class CreditControlPolicyLevel(models.Model):
    _inherit = "credit.control.policy.level"

    custom_text = fields.Html(string='Custom Message',
                              required=True,
                              translate=True)
    custom_text_after_details = fields.Html(
        string='Custom Message after details', translate=True)
