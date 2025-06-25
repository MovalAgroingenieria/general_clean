# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


class LawMeasuringDeviceMeasurement(models.Model):
    _name = 'law.measuring.device.measurement'
    _description = 'Law Measuring Device Measurement'

    measuring_device_id = fields.Many2one(
        comodel_name='law.measuring.device',
        required=True,
        string='Measuring Device ID',
        index=True,
        ondelete='restrict',
    )

    measurement_time = fields.Datetime(
        string='Measurement Time',
        required=True,
    )

    value = fields.Float(
        string='Measurement Value',
        digits=(32, 4),
        required=True,
    )

    uom_id = fields.Many2one(
        comodel_name='law.parameter.uom',
        string='Unit of Measure',
    )

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
        compute='_compute_name',
    )

    sql_constraints = [
        ('name_unique', 'unique(name)',
         'The analysis parameter must be unique.'),
    ]

    @api.depends('measuring_device_id', 'measuring_device_id.name',
                 'measurement_time')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.measuring_device_id and record.measuring_device_id.name \
                    and record.measurement_time:
                name = record.measuring_device_id.name + ' - ' + \
                    record.measurement_time
            record.name = name
