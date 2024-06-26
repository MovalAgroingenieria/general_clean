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
            self.env.context.get("company_id", self.env.user.company_id.id)
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

    @api.model
    def create(self, vals):
        record = super(LawAnalysis, self).create(vals)
        if 'laboratory_id' in vals:
            laboratory_id = vals['laboratory_id']
            laboratory = self.env['res.partner'].browse(laboratory_id)
            if laboratory.exists():
                laboratory.write({'supplier': True})

        return record
