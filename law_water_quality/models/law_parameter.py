# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class LawParameter(models.Model):
    _name = "law.parameter"
    _description = "Law Parameter"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )

    uom_id = fields.Many2one(
        comodel_name="law.parameter.uom",
        string="Unit of Measure",
        required=True,
        index=True,
        ondelete="restrict",
    )

    analysis_procedure = fields.Char(
        string="Analysis Procedure",
        required=True,
        index=True,
    )

    with_maximum_value_admissible = fields.Boolean(
        string="With VMA",
        required=True,
        default=True,
    )

    maximum_value_admissible = fields.Float(
        string="Maximum Value Admissible (VMA)",
        digits=(32, 6),
        default=0.0,
    )

    with_maximum_deviation_admissible = fields.Boolean(
        string="With DMA",
        required=True,
        default=True,
    )

    maximum_deviation_admissible = fields.Float(
        string="Maximum Deviation Admisible (DMA)",
        digits=(32, 6),
        default=0.0,
    )

    notes = fields.Html(
        string="Notes",
    )

    notes_text = fields.Char(
        string="Notes (as text)",
        store=True,
        index=True,
        readonly=True,
        compute="_compute_notes_text",
    )

    analysis_parameter_ids = fields.One2many(
        comodel_name="law.analysis.parameter",
        inverse_name="parameter_id",
        string="Analysis Parameters",
    )

    sql_constraints = [
        ("name_unique", "unique(name)",
         "The parameter must be unique."),
    ]

    @api.depends("notes")
    def _compute_notes_text(self):
        model_converter = self.env["ir.fields.converter"]
        for record in self:
            notes_text = ""
            if record.notes:
                notes_text = model_converter.text_from_html(
                    record.notes, 50, 150)
            record.notes_text = notes_text

    @api.onchange("with_maximum_value_admissible")
    def _onchange_with_maximum_value_admissible(self):
        if not self.with_maximum_value_admissible:
            self.maximum_value_admissible = 0.0

    @api.onchange("with_maximum_deviation_admissible")
    def _onchange_with_maximum_deviation_admissible(self):
        if not self.with_maximum_deviation_admissible:
            self.maximum_deviation_admissible = 0.0

    @api.model
    def create(self, vals):
        if not vals.get("with_maximum_value_admisible", True):
            vals["maximum_value_admisible"] = 0.0
        if not vals.get("with_maximum_deviation_admisible", True):
            vals["maximum_deviation_admisible"] = 0.0
        return super(LawParameter, self).create(vals)

    def write(self, vals):
        if not vals.get("with_maximum_value_admisible", True):
            vals["maximum_value_admisible"] = 0.0
        if not vals.get("with_maximum_deviation_admisible", True):
            vals["maximum_deviation_admisible"] = 0.0
        return super(LawParameter, self).write(vals)

    @api.multi
    def action_see_parameter_analysis(self):
        self.ensure_one()
        condition = [('parameter_id', '=', self.id)]
        id_tree_view = self.env.ref(
            'law_water_quality.law_analysis_parameter_view_tree').id
        search_view = self.env.ref(
            'law_water_quality.law_analysis_parameter_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Analysis Parameters'),
            'res_model': 'law.analysis.parameter',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree')],
            'search_view_id': (search_view.id, search_view.name),
            'domain': condition,
            'target': 'current',
            'context': '{\'create\': False, \'edit\': False}',
        }
        return act_window
