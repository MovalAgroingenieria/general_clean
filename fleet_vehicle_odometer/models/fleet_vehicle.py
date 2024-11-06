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

    @api.depends('value', 'initial_value')
    def _compute_qty_odometer_kms(self):
        for record in self:
            record.quantity = record.value - record.initial_value
