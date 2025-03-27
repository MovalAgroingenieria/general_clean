# -*- coding: utf-8 -*-
# Copyright 2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'
    
    nif_issuing_organisation = fields.Char(
        string="NIF Issuing Organisation",
        help="NIF of the organisation that issues the file")
    
    issuring_name = fields.Char(
        string="Issuring Name",
        help="Name of the organisation that issues the file")
    
    @api.multi
    def set_nif_issuing_organisation_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'nif_issuing_organisation',
            self.nif_issuing_organisation)
   
    @api.multi
    def set_issuring_name_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'issuring_name',
            self.issuring_name)


