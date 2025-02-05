# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class LawAnalysis(models.Model):
    _name = "law.analysis"
    _description = "Law Analysis"
    _inherit = ["mail.thread"]

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

    name = fields.Char(
        string="Sample Code",
        required=True,
        index=True,
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
        selection=[("01_client",
                    "Client"),
                   ("02_laboratory",
                    "Laboratory")],
        index=True,
        default="01_client",
        required=True,
    )

    collection_time = fields.Datetime(
        string="Collection Time",
        index=True,
        required=True,
    )

    receival_time = fields.Datetime(
        string="Receival Time",
        index=True,
    )

    analysis_start_time = fields.Datetime(
        string="Analysis Start Time",
    )

    analysis_end_time = fields.Datetime(
        string="Analysis End Time",
    )

    notes = fields.Html(
        string="Notes",
    )

    analysis_parameter_ids = fields.One2many(
        comodel_name="law.analysis.parameter",
        inverse_name="analysis_id",
        string="Analysis Parameters",
    )

    analysis_template_id = fields.Many2one(
        string='Analysis Template',
        comodel_name="law.analysis.template",
        ondelete='restrict',
    )

    analysis_receival_time = fields.Datetime(
        string='Analysis Receival Date',
    )

    analysis_invoiced = fields.Boolean(
        string='Analysis Invoiced',
        default=False,
    )

    invoice_number = fields.Char(
        string='Invoice Number',
    )

    invoiced_quantity = fields.Float(
        string='Invoiced Quantity',
        digits=(32, 2),
        default=0.0,
    )

    expected_invoiced_quantity = fields.Float(
        string='Expected Invoiced Quantity',
        digits=(32, 2),
        default=0.0,
    )

    _sql_constraints = [
        ("sample_code_unique", "unique(sample_code)",
         "The analysis must be unique."),
        ("collection_time_before_receival_time",
         "CHECK(collection_time <= receival_time)",
         "The collection time must be before the receival time."),
        ("analysis_start_time_before_analysis_end_time",
         "CHECK(analysis_start_time <= analysis_end_time)",
         "The analysis start time must be before the analysis end time."),
    ]

    @api.onchange('analysis_template_id')
    def _onchange_analysis_template_id(self):
        if self.analysis_template_id:
            template = self.analysis_template_id
            self.client_id = template.client_id
            self.laboratory_id = template.laboratory_id
            self.location = template.location
            self.watertype_id = template.watertype_id
            self.coordinate_x = template.coordinate_x
            self.coordinate_y = template.coordinate_y
            self.coordinate_srs = template.coordinate_srs
            self.sample_taker = template.sample_taker
            self.expected_invoiced_quantity = \
                template.expected_invoiced_quantity
            new_parameters = []
            for parameter in template.parameter_ids:
                new_parameters.append((0, 0, {
                    'parameter_id': parameter.parameter_id.id,
                    'analysis_procedure':
                        parameter.parameter_id.analysis_procedure,
                    'result_value': 0.0,
                }))
            self.analysis_parameter_ids = new_parameters

    @api.model
    def create(self, vals):
        record = super(LawAnalysis, self).create(vals)
        if 'laboratory_id' in vals:
            laboratory_id = vals['laboratory_id']
            laboratory = self.env['res.partner'].browse(laboratory_id)
            if laboratory.exists():
                laboratory.write({'supplier': True})

        return record
