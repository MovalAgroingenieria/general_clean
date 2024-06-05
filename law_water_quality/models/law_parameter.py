# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LawParameter(models.Model):
    _name = "law.parameter"
    _description = "Law Parameter"

    name = fields.Char(
        string="Name",
        required=True,
        index=True)

    uom_id = fields.Many2one(
        comodel_name="law.parameter.uom",
        string="Unit of Measure",
        required=True,
        index=True,
        ondelete='restrict')

    analysis_procedure = fields.Char(
        string="Analysis Procedure",
        required=True,
        index=True)

    with_maximum_value_admissible = fields.Boolean(
        string="With VMA",
        required=True,
        default=True)

    maximum_value_admissible = fields.Float(
        string="Maximum Value Admissible (VMA)",
        digits=(32, 6),
        required=False,
        default=0.0)

    with_maximum_deviation_admissible = fields.Boolean(
        string="With DMA",
        required=True,
        default=True)

    maximum_deviation_admissible = fields.Float(
        string="Maximum Deviation Admisible (DMA)",
        digits=(32, 6),
        required=False,
        default=0.0)

    notes = fields.Html(
        string="Notes")

    notes_text = fields.Char(
        string="Notes (as text)",
        store=True,
        index=True,
        readonly=True,
        compute='_compute_notes_text',
    )

    analysis_parameter_ids = fields.One2many(
        comodel_name="law.analysis.parameter",
        inverse_name="parameter_id",
        string="Analysis Parameters",
        required=False
    )

    sql_constraints = [
        ('name_unique', 'unique(name)',
         'The name must be unique!')
    ]

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if self.search([
                ('name', '=', record.name),
                ('id', '!=', record.id)
            ]):
                raise ValidationError("The name must be unique!")

    @api.model
    def create(self, vals):
        if not vals.get('with_maximum_value_admisible', True):
            vals['maximum_value_admisible'] = 0.0
        if not vals.get('with_maximum_deviation_admisible', True):
            vals['maximum_deviation_admisible'] = 0.0
        return super(LawParameter, self).create(vals)

    def write(self, vals):
        if not vals.get('with_maximum_value_admisible', True):
            vals['maximum_value_admisible'] = 0.0
        if not vals.get('with_maximum_deviation_admisible', True):
            vals['maximum_deviation_admisible'] = 0.0
        return super(LawParameter, self).write(vals)

    def _compute_notes_text(self):
        model_converter = self.env["ir.fields.converter"]
        for record in self:
            notes_text = ''
            if record.notes:
                notes_text = model_converter.text_from_html(
                    record.notes, 50, 150)
            record.notes_text = notes_text
