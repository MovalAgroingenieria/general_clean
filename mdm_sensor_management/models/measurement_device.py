# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class MeasurementDevice(models.Model):
    _name = 'mdm.measurement.device'
    _description = 'Measurement Device'
    _order = 'name'

    name = fields.Char(
        string='Identifier',
        required=True,
        index=True,
    )

    description = fields.Text(
        string='Description',
    )

    notes = fields.Html(
        string='Notes',
    )

    attributes = fields.Html(
        string='Attributes',
    )

    location = fields.Char(
        string='Location',
    )

    brand = fields.Char(
        string='Brand',
    )

    model = fields.Char(
        string='Model',
    )

    serial_number = fields.Char(
        string='Serial Number',
    )

    installation_date = fields.Date(
        string='Installation Date',
    )

    photo = fields.Binary(
        string='Photo',
        attachment=True,
    )

    sensor_ids = fields.One2many(
        comodel_name='mdm.measurement.device.sensor',
        inverse_name='device_id',
        string='Sensors',
    )

    reading_ids = fields.One2many(
        comodel_name='mdm.measurement.device.sensor.reading',
        inverse_name='device_id',
        string='Readings',
    )

    sensor_count = fields.Integer(
        string='Sensors',
        compute='_compute_sensor_count',
        store=True,
    )

    reading_count = fields.Integer(
        string='Readings',
        compute='_compute_reading_count',
        store=True,
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The identifier must be unique.'),
    ]

    def action_view_sensors(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sensors',
            'res_model': 'mdm.measurement.device.sensor',
            'view_mode': 'tree,form',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_device_id': self.id},
        }

    def action_view_readings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Readings',
            'res_model': 'mdm.measurement.device.sensor.reading',
            'view_mode': 'tree,form,pivot',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_device_id': self.id},
        }

    @api.depends('sensor_ids')
    def _compute_sensor_count(self):
        for rec in self:
            rec.sensor_count = len(rec.sensor_ids)

    @api.depends('reading_ids')
    def _compute_reading_count(self):
        for rec in self:
            rec.reading_count = len(rec.reading_ids)
