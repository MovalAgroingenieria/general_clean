# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LawMeasuringDeviceType(models.Model):
    _inherit = 'law.measuring.device.type'

    remotecontrol_measurement_transformation = fields.Char(
        string='Measurement Transformation',
        required=True,
        default='$',
    )

    remotecontrol_enabled = fields.Boolean(
        string='Remote Control enabled',
        compute='_compute_remotecontrol_enabled',
    )

    @api.multi
    def _compute_remotecontrol_enabled(self):
        remotecontrol_enabled = self.env['ir.values'].get_default(
            'law.measuring.configuration', 'remotecontrol_enabled')
        if remotecontrol_enabled is None:
            remotecontrol_enabled = False
        self.write({'remotecontrol_enabled': remotecontrol_enabled})
