# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class ResStreetTypeConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.street.type.configuration'

    def _default_current_address_format(self):
        logged_user = self.env.user
        current_address_format = logged_user.country_id.address_format
        return current_address_format

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
        default=_default_current_address_format,
        help="This field shows the current address format for user country.\n\
            You can change it with the python-style string pattern with all \
            address fields:\n%(street_type_show)s: the street type\n\
            %(state_name)s: the name of the state\n\%(state_code)s: the code\
            of the state\n%(country_name)s: the name of the country\n\
            %(country_code)s: the code of the country.\nThis format will be \
            apply to all countries but later it can be individualized by \
            country. Errors in the format are not detected.")

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('res.street.type.configuration',
                           'street_type_shown', self.street_type_shown)
        new_format = self.address_format_set
        query = """UPDATE res_country SET address_format = '%s'""" % new_format
        self.env.cr.execute(query)
