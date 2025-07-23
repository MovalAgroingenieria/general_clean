# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class MeasurementDeviceSensorReading(models.Model):
    _name = 'mdm.measurement.device.sensor.reading'
    _description = 'Measurement Device Sensor Reading'
    _order = 'sensor_id, measurement_time desc'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        index=True,
    )

    device_id = fields.Many2one(
        string='Measurement Device',
        comodel_name='mdm.measurement.device',
        compute='_compute_device_id',
        store=True,
        index=True,
        ondelete='restrict',
    )

    sensor_id = fields.Many2one(
        comodel_name='mdm.measurement.device.sensor',
        string='Sensor',
        required=True,
        index=True,
        ondelete='restrict',
    )

    measurement_time = fields.Datetime(
        string='Measurement Time',
        required=True,
    )

    value = fields.Float(
        string='Value',
        required=True,
        digits=(32, 4),
    )

    uom_id = fields.Many2one(
        comodel_name='mdm.measurement.device.sensor.uom',
        string='Unit of Measure',
        related='sensor_id.uom_id',
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The sensor reading must be unique.'),
    ]

    @api.depends('device_id.name', 'measurement_time')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.device_id and record.measurement_time:
                name = '%s - %s' % (
                    record.device_id.name, record.measurement_time)
            record.name = name

    @api.depends('sensor_id')
    def _compute_device_id(self):
        for record in self:
            device_id = None
            if record.sensor_id and record.sensor_id.device_id:
                device_id = record.sensor_id.device_id
            record.device_id = device_id
