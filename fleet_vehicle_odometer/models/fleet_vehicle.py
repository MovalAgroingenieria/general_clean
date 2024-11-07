# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.osv import expression


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    _description = 'Odometer log for a vehicle'
 
    initial_value = fields.Float('Initial Odometer Value', group_operator="max")
    project_id = fields.Many2one('project.project', 'Project', required=True)
    quantity = fields.Float('Quantity', compute='_compute_qty_odometer_kms')
    driver_id = fields.Many2one('res.partner', string='Driver', tracking=True,
                                help='Driver of the trip', copy=False,
                                default=lambda self: self._default_driver_id()
    )

    @api.model
    def _default_driver_id(self):
        return self.vehicle_id.driver_id.id \
            if (self.vehicle_id and self.vehicle_id.driver_id) else False

    @api.depends('value', 'initial_value')
    def _compute_qty_odometer_kms(self):
        for record in self:
            record.quantity = record.value - record.initial_value
