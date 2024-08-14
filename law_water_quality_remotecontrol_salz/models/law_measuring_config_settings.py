# -*- coding: utf-8 -*-
# 2024 - Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LawMeasuringConfiguration(models.TransientModel):
    _inherit = 'law.measuring.configuration'

    url_remote_api_rest_salz = fields.Char(
        string='API REST URL',
        size=255,
    )

    url_remote_api_rest_username_salz = fields.Char(
        string='Username',
        size=255,
        help='Username for authentication in remote API',
    )

    url_remote_api_rest_password_salz = fields.Char(
        string='Password',
        size=255,
        help='Password for authentication in remote API',
    )

    url_remote_app_salz = fields.Char(
        string='APP Salz URL',
        size=255,
    )

    @api.multi
    def set_default_values(self):
        super(LawMeasuringConfiguration, self).set_default_values()
        values = self.env['ir.values'].sudo()
        values.set_default('law.measuring.configuration',
                           'url_remote_api_rest_salz',
                           self.url_remote_api_rest_salz)
        values.set_default('law.measuring.configuration',
                           'url_remote_api_rest_username_salz',
                           self.url_remote_api_rest_username_salz)
        values.set_default('law.measuring.configuration',
                           'url_remote_api_rest_password_salz',
                           self.url_remote_api_rest_password_salz)
        values.set_default('law.measuring.configuration',
                           'url_remote_app_salz',
                           self.url_remote_app_salz)
        return values
