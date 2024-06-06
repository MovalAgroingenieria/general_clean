# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LawAnalysisParameter(models.Model):
    _name = "law.analysis.parameter"
    _description = "Law Analysis Parameter"

    name = fields.Char(
        string="Name",
        index=True,
        compute="_compute_name",
    )

    analysis_id = fields.Many2one(
        comodel_name="law.analysis",
        string="Analysis",
        required=True,
        index=True,
        ondelete="cascade",
    )

    parameter_id = fields.Many2one(
        comodel_name="law.parameter",
        string="Parameter",
        required=True,
        index=True,
        ondelete="restrict",
    )

    parameter_uom_id = fields.Many2one(
        comodel_name="law.parameter.uom",
        string="Unit of Measure",
        index=True,
        ondelete="restrict",
        related="parameter_id.uom_id",
        readonly=True,
        store=True,
    )

    parameter_maximum_value_admissible = fields.Float(
        string="Parameter Maximum Value Admissible",
        digits=(32, 6),
        related="parameter_id.maximum_value_admissible",
        readonly=True,
        store=True,
    )

    result_value = fields.Float(
        string="Result Value",
        digits=(32, 6),
        required=True,
        default=0.0,
    )

    analysis_procedure = fields.Char(
        string="Analysis Procedure",
        required=True,
        index=True,
    )

    parameter_value_above_mav = fields.Boolean(
        string="Value Above MAV",
        index=True,
        store=True,
        compute="_compute_parameter_value_above_mav",
    )

    notes = fields.Char(
        string="Notes",
    )

    sql_constraints = [
        ("name_unique", "unique(name)",
         "The analysis parameter must be unique."),
    ]

    @api.depends("analysis_id", "analysis_id.name", "parameter_id",
                 "parameter_id.name")
    def _compute_name(self):
        for record in self:
            name = ""
            if (record.analysis_id and record.parameter_id):
                name = record.analysis_id.name + u"-" +\
                    record.parameter_id.name
            record.name = name

    def name_get(self):
        result = []
        for record in self:
            display_name = ""
            if (record.analysis_id and record.parameter_id):
                display_name = record.analysis_id.name +\
                    u" (" + record.parameter_id.name + u")"
            result.append((record.id, display_name))
        return result

    @api.depends("result_value", "parameter_id",
                 "parameter_id.with_maximum_value_admissible",
                 "parameter_id.maximum_value_admissible")
    def _compute_parameter_value_above_mav(self):
        for record in self:
            parameter_value_above_mav = False
            if (record.parameter_id.with_maximum_value_admissible and
                    (record.result_value >
                     record.parameter_id.maximum_value_admissible)):
                parameter_value_above_mav = True
            record.parameter_value_above_mav = parameter_value_above_mav

    @api.onchange("parameter_id")
    def _onchange_parameter_id(self):
        if self.parameter_id:
            self.analysis_procedure = self.parameter_id.analysis_procedure
