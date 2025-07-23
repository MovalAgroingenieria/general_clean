# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class MeasurementDeviceSensorUOM(models.Model):
    _name = 'mdm.measurement.device.sensor.uom'
    _description = 'Sensor Unit of Measure'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
    )

    short_name = fields.Char(
        string='Short Name',
        index=True,
    )

    description = fields.Char(
        string='Description',
    )

    notes = fields.Html(
        string='Notes',
    )

    sensor_ids = fields.One2many(
        comodel_name='mdm.measurement.device.sensor',
        inverse_name='uom_id',
        string='Sensors',
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The unit of measure must be unique.'),
        ('unique_short_name', 'unique(short_name)',
         'The short name must be unique.'),
    ]

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.short_name:
                display_name = "%s (%s)" % (record.name, record.short_name)
            else:
                display_name = record.name
            result.append((record.id, display_name))
        return result
