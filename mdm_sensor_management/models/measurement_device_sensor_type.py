# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class MeasurementDeviceSensorType(models.Model):
    _name = 'mdm.measurement.device.sensor.type'
    _description = 'Sensor Type'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
    )
    description = fields.Text(
        string='Description',
    )

    uom_id = fields.Many2one(
        comodel_name='mdm.measurement.device.sensor.uom',
        string='Unit of Measure',
        required=True,
        ondelete='restrict',
    )

    sensor_ids = fields.One2many(
        comodel_name='mdm.measurement.device.sensor',
        inverse_name='type_id',
        string='Sensors',
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The sensor type must be unique.'),
    ]
