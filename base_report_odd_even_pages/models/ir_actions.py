# -*- coding: utf-8 -*-
# Copyright 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_page_adjustment = fields.Selection([
        ('default', 'Default'),
        ('ensure_odd', 'Ensure odd'),
        ('ensure_even', 'Ensure even')],
        required=True,
        default="default")
