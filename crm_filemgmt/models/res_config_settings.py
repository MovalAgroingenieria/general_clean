# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class FileConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Configuration of File Management'

    annual_seq_prefix = fields.Char(
        string='Prefix (annual seq.)',
        size=10,
        config_parameter='crm_filemgmt.annual_seq_prefix',)
