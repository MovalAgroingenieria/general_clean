# -*- coding: utf-8 -*-
# 2024 - Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class LawMeasuringConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'law.measuring.configuration'
    _description = 'Configuration of wua_law_water_quality module'

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        return values
