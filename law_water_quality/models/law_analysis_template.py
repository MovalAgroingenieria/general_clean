# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LawAnalysisTemplate(models.Model):
    _name = 'law.analysis.template'
    _description = 'Templates for Law Analysis'

    name = fields.Char(
        string="Analysis Template",
        required=True,
        index=True,
    )

    client_id = fields.Many2one(
        comodel_name="res.partner",
        string="Client",
        required=True,
        default=lambda self: self.env["res.company"].browse(
            self.env.context.get("company_id", self.env.user.company_id.id),
            ).partner_id.id,
        readonly=True,
    )

    laboratory_id = fields.Many2one(
        comodel_name="res.partner",
        string="Laboratory",
        domain=[("supplier", "=", True)],
        required=True,
    )

    location = fields.Char(
        string="Location",
    )

    watertype_id = fields.Many2one(
        comodel_name="law.watertype",
        string="Water Type",
        required=True,
        index=True,
        ondelete="restrict",
    )

    coordinate_x = fields.Float(
        string="Coordinate X",
        digits=(32, 6),
    )

    coordinate_y = fields.Float(
        string="Coordinate Y",
        digits=(32, 6),
    )

    coordinate_srs = fields.Char(
        string="Coordinate System",
        default="EPSG:25830",
    )

    sample_taker = fields.Selection(
        string="Sample Taker",
        selection=[("01_client", "Client"),
                   ("02_laboratory", "Laboratory")],
        index=True,
        default="01_client",
        required=True,
    )

    expected_invoiced_quantity = fields.Float(
        string='Expected Invoiced Quantity',
        digits=(32, 2),
        default=0.0,
    )

    interval_days = fields.Integer(
        string='Frecuency (Days)',
        default=0,
    )

    notes = fields.Html(
        string="Notes",
    )

    parameter_ids = fields.One2many(
        string='Parameters',
        comodel_name='law.analysis.template.parameter.rel',
        inverse_name='analysis_template_id',
    )

    analysis_ids = fields.One2many(
        string="Analysis",
        comodel_name="law.analysis",
        inverse_name="analysis_template_id",
    )

    @api.multi
    def action_show_parameters_form(self):
        self.ensure_one()
        id_tree_view = self.env.ref(
            'law_water_quality.law_analysis_view_tree').id
        act_window = {
            'type': 'ir.actions.act_window',
            'name': ('Analysis'),
            'res_model': 'law.analysis',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree')],
            'target': 'current',
            'domain': [('id', 'in', self.analysis_ids.ids)],
            }
        return act_window
