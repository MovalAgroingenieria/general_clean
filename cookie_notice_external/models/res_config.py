# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    cookie_service_script = fields.Text(
        string="Cookie script",
        help="Copy here the script of your cookie provider.")

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default(
            'website.config.settings', 'cookie_service_script',
            self.cookie_service_script)
