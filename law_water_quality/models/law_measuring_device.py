# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _


class LawMeasuringDevice(models.Model):
    _name = 'law.measuring.device'
    _description = 'Law Measuring Device'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
    )

    measuring_device_type_id = fields.Many2one(
        comodel_name='law.measuring.device.type',
        string='Measuring Device Type',
        required=True,
        index=True,
        ondelete='restrict',
    )

    uom_id = fields.Many2one(
        comodel_name='law.parameter.uom',
        string='Unit of Measure',
        related='measuring_device_type_id.uom_id',
        readonly=True,
        store=True
    )

    description = fields.Char(
        string='Description',
    )

    measurement_ids = fields.One2many(
        comodel_name='law.measuring.device.measurement',
        inverse_name='measuring_device_id',
        string='Measurements'
    )

    number_of_measurements = fields.Integer(
        string='N. of measurements',
        compute='_compute_number_of_measurements')

    last_measurement_time = fields.Datetime(
        string='Last measurement',
        compute='_compute_last_measurement')

    last_measurement_value = fields.Float(
        string='Last Measurement Value',
        digits=(32, 4),
        compute='_compute_last_measurement'
    )

    active = fields.Boolean(
        default=True
    )

    notes = fields.Html(
        string='Notes',
    )

    sql_constraints = [
        ("name_unique", "unique(name)",
         "The analysis parameter must be unique."),
    ]

    @api.depends('measurement_ids.measurement_time')
    def _compute_last_measurement(self):
        for record in self:
            last_measurement = self.env['law.measuring.device.measurement']\
                .search([('measuring_device_id', '=', record.id)
                         ], order='measurement_time desc', limit=1)
            if last_measurement:
                record.write({
                    'last_measurement_time': last_measurement.measurement_time,
                    'last_measurement_value': last_measurement.value
                })
            else:
                record.write({
                    'last_measurement_time': False,
                    'last_measurement_value': False
                })

    @api.multi
    def _compute_number_of_measurements(self):
        for record in self:
            record.number_of_measurements = len(record.measurement_ids)

    @api.multi
    def action_show_measuring_device_measurement(self):
        self.ensure_one()
        id_tree_view = self.env.ref(
            'law_water_quality.law_measuring_device_measurement_view_tree').id
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Measurements'),
            'res_model': 'law.measuring.device.measurement',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree')],
            'target': 'current',
            'domain': [('id', 'in', self.measurement_ids.ids)],
            }
        return act_window
