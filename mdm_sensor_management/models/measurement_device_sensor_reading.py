# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class MeasurementDeviceSensorReading(models.Model):
    _name = 'mdm.measurement.device.sensor.reading'
    _description = 'Measurement Device Sensor Reading'
    _order = 'measurement_time desc'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        required=True,
        index=True,
    )

    device_id = fields.Many2one(
        comodel_name='mdm.measurement.device',
        string='Measurement Device',
        required=True,
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
        for rec in self:
            rec.name = '%s - %s' % (
                rec.device_id.name or '',
                rec.measurement_time or '')

    @api.onchange('device_id', 'measurement_time')
    def _onchange_name(self):
        for rec in self:
            rec.name = '%s - %s' % (
                rec.device_id.name or '',
                rec.measurement_time or '')

    @api.model
    def create(self, vals):
        if 'device_id' in vals or 'measurement_time' in vals:
            device = self.env['mdm.measurement.device'].browse(
                vals.get('device_id'))
            vals['name'] = '%s - %s' % (
                device.name or '',
                vals.get('measurement_time') or '')
        return super(MeasurementDeviceSensorReading, self).create(vals)

    def write(self, vals):
        if 'device_id' in vals or 'measurement_time' in vals:
            for rec in self:
                device = rec.device_id
                if 'device_id' in vals:
                    device = self.env['mdm.measurement.device'].browse(
                        vals['device_id'])
                mtime = vals.get('measurement_time', rec.measurement_time)
                vals_name = '%s - %s' % (device.name or '', mtime or '')
                vals['name'] = vals_name
        return super(MeasurementDeviceSensorReading, self).write(vals)
