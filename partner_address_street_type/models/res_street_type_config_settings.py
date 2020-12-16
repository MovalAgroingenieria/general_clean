# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.street.type.configuration'
    _description = 'Street type settings'

    street_type_shown = fields.Selection([
        ("not_show", "Not show"),
        ("short", "Abbreviation"),
        ("long", "Name")],
        string="Street type shown",
        required=True,
        default="long",
        help="Determine how the street type will be displayed.")

    address_format_set = fields.Text(
        string="Address format",
        default=lambda self: self.env['res.country'].search(
            [('code', '=', self.env.company.country_id.code)],
            limit=1).address_format,
        help="This field shows the current address format for company country.\
            You can change it with the python-style string pattern with all \
            address fields.\nThis format will be apply to company country.\n\
            Errors in the format are not detected.")

    def set_values(self):
        IrDefault = self.env['ir.default']
        IrDefault.set('res.street.type.configuration','street_type_shown',
                      self.street_type_shown)
        if self.address_format_set:
            company_country_code = self.env['res.country'].search(
                [('code', '=', self.env.company.country_id.code)],limit=1).code
            new_format = self.address_format_set
            query = f"""UPDATE res_country
                        SET address_format = '{new_format}'
                        WHERE code = '{company_country_code}';"""
            self.env.cr.execute(query)
