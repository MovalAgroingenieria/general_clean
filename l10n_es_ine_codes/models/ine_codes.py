# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class IneCodes(models.Model):
    _name = "res.ine.codes"
    _description = "Codes for cities in the INE \
        (Spanish Statistics National Institute)"

    ine_code_state = fields.Char(string="State INE code")
    ine_code_province = fields.Integer(string="Province INE code")
    ine_code_city = fields.Integer(string="City INE code")
    city_name = fields.Char(string="City")
    city_name_simplified = fields.Char(string="City simplified")
    city_name_aka = fields.Char(string="City alternative name")
    city_name_aka_simplified = fields.Char(
        string="City alternative name simplified")
    city_name_reordered = fields.Char(string="City reordered name")
    city_name_reordered_simplified = fields.Char(
        string="City reordered name simplified")

    @api.model
    def read_group(self, domain, fields, groupby,
                   offset=0, limit=None, orderby=False, lazy=True):
        if 'ine_code_state' in groupby and 'ine_code_province' in groupby:
            fields_to_remove = ['ine_code_city']
        elif 'ine_code_state' in groupby:
            fields_to_remove = ['ine_code_province','ine_code_city']
        elif 'ine_code_province' in groupby:
            fields_to_remove = ['ine_code_state','ine_code_city']
        else:
            fields_to_remove = []
        for field_to_remove in fields_to_remove:
            if field_to_remove in fields:
                fields.remove(field_to_remove)
        return super(IneCodes, self).read_group(
            domain, fields, groupby, offset, limit, orderby, lazy)
