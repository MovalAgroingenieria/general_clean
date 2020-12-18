# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class FileConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.file.config.settings'
    _description = 'Configuration of File Management'

    annual_seq_prefix = fields.Char(
        string='Prefix (annual seq.)',
        size=10,
        help='Default Code for Files: <prefix>/<year>/num')

    def set_values(self):
        IrDefault = self.env['ir.default']
        IrDefault.set('res.file.config.settings', 'annual_seq_prefix',
                      self.annual_seq_prefix)