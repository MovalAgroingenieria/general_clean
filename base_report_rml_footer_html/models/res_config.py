# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = "account.config.settings"
    company_footer = fields.Html(
        related='company_id.rml_footer',
        string='Bank accounts footer preview',
        readonly=True,
        help="Bank accounts as printed in the footer of each printed document",
    )


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"

    rml_footer = fields.Html(
        string='Custom Report Footer *',
        related="company_id.rml_footer",
        help="Footer text displayed at the bottom of all reports.",
    )

    rml_footer_readonly = fields.Html(
        string='Report Footer *',
        related='rml_footer',
        readonly=True,
    )
