# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class FileConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.file.config.settings'
    _description = 'Configuration of File Management'

    default_annual_seq_prefix = fields.Char(
        string='Prefix (annual seq.)',
        size=10,
        help='Default Code for Files: <prefix>/<year>/num')

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('res.file.config.settings',
                           'default_annual_seq_prefix',
                           self.default_annual_seq_prefix)
