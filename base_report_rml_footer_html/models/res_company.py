# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    rml_footer = fields.Html(
        string='Custom Report Footer',
        translate=True,
        help="Footer text displayed at the bottom of all reports.",
    )

    rml_footer_readonly = fields.Html(
        related='rml_footer',
        string='Report Footer',
        readonly=True,
    )
