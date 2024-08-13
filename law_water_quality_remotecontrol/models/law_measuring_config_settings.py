# -*- coding: utf-8 -*-
# 2024 - Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LawMeasuringConfiguration(models.TransientModel):
    _inherit = 'law.measuring.configuration'

    remotecontrol_enabled = fields.Boolean(
        string='Remotecontrol Enabled',)

    @api.multi
    def set_default_values(self):
        super(LawMeasuringConfiguration, self).set_default_values()
        values = self.env['ir.values'].sudo()
        values.set_default('law.measuring.configuration',
                           'remotecontrol_enabled',
                           self.remotecontrol_enabled)
        return values
