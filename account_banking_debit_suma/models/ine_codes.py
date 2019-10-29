# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


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
