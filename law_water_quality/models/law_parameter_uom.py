# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LawParameterUom(models.Model):
    _name = "law.parameter.uom"
    _description = "Law Parameter Unit of Measure"

    name = fields.Char(
        string="Name",
        required=True,
        index=True)

    short_name = fields.Char(
        string="Short Name",
        required=True,
        index=True)

    description = fields.Char(
        string="Description",
        required=False)

    parameter_ids = fields.One2many(
        comodel_name="law.parameter",
        inverse_name="uom_id",
        string="Parameters",
        required=False)

    notes = fields.Html(
        string="Notes",
        required=False)

    sql_constraints = [
        ('name_unique', 'unique(name)',
         'The name must be unique!'),
        ('short_name_unique', 'unique(short_name)',
         'The short name must be unique!')
    ]

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if self.search([
                ('name', '=', record.name),
                ('id', '!=', record.id)
            ]):
                raise ValidationError("The name must be unique!")

    @api.constrains('short_name')
    def _check_unique_short_name(self):
        for record in self:
            if self.search([
                ('short_name', '=', record.short_name),
                ('id', '!=', record.id)
            ]):
                raise ValidationError("The short name must be unique!")

    def name_get(self):
        result = []
        for record in self:
            name = record.name or ''
            short_name = record.short_name or ''
            display_name = "{} ({})".format(name, short_name)
            result.append((record.id, display_name))
        return result
