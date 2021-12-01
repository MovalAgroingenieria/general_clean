# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LetterConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.letter.config.settings'
    _description = 'Configuration of Register Management'

    enable_access_res_letter_portal_user = fields.Boolean(
        string='Enable access of portal user to register management',
        default=True,
        help='Grant or revoke access of portal users to register management')

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('res.letter.config.settings',
                           'enable_access_res_letter_portal_user',
                           self.enable_access_res_letter_portal_user)
