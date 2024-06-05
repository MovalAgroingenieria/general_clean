# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LawWatertype(models.Model):
    _name = "law.watertype"
    _description = "Law Watertype"

    name = fields.Char(string="Name",
                       required=True,
                       index=True)

    description = fields.Char(string="Description",
                              required=False,
                              index=True)

    analysis_ids = fields.One2many(
        comodel_name="law.analysis",
        inverse_name="watertype_id",
        string="Analysis",
        required=False)

    notes = fields.Html(string="Notes",
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
