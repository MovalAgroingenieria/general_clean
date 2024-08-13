# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class LawMeasuringDeviceType(models.Model):
    _name = 'law.measuring.device.type'
    _description = 'Law Measuring Device Type'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
    )

    uom_id = fields.Many2one(
        comodel_name='law.parameter.uom',
        string='Unit of Measure',
        required=True,
        index=True,
        ondelete='restrict',
    )

    description = fields.Char(
        string='Description',
    )

    device_ids = fields.One2many(
        comodel_name='law.measuring.device',
        inverse_name='measuring_device_type_id',
        string='Devices'
    )

    notes = fields.Html(
        string='Notes',
    )

    sql_constraints = [
        ("name_unique", "unique(name)",
         "The analysis parameter must be unique."),
    ]
