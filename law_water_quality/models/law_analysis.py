# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class LawAnalysis(models.Model):
    _name = "law.analysis"
    _description = "Law Analysis"
    _inherit = ['mail.thread']

    client_id = fields.Many2one(
        comodel_name="res.partner",
        string="Client",
        required=True,
        default=lambda self: self.env['res.company'].browse(
            self.env.context.get('company_id', self.env.user.company_id.id)
        ).partner_id.id)

    laboratory_id = fields.Many2one(
        comodel_name="res.partner",
        string="Laboratory",
        domain=[('supplier', '=', True)],
        required=True)

    location = fields.Char(
        string="Location",
        required=False)

    name = fields.Char(
        string="Name",
        required=True,
        index=True)

    watertype_id = fields.Many2one(
        comodel_name="law.watertype",
        string="Water Type",
        required=True,
        index=True,
        ondelete='restrict')

    coordinate_x = fields.Float(
        string="Coordinate X",
        digits=(32, 6),
        required=False)

    coordinate_y = fields.Float(
        string="Coordinate Y",
        digits=(32, 6),
        required=False)

    coordinate_srs = fields.Char(
        string="Coordinate System",
        default="EPSG:25830",
        required=False)

    sample_taker = fields.Selection(
        string="Sample Taker",
        selection=[('00_client',
                    'Client'),
                   ('01_laboratory',
                    'Laboratory')],
        index=True,
        default='00_client',
        required=True)

    collection_time = fields.Datetime(
        string="Collection Time",
        index=True,
        required=True)

    receival_time = fields.Datetime(
        string="Receival Time",
        index=True,
        required=False)

    analysis_start_time = fields.Datetime(
        string="Analysis Start Time",
        required=False)

    analysis_end_time = fields.Datetime(
        string="Analysis End Time",
        required=False)

    notes = fields.Html(
        string="Notes",
        required=False)

    analysis_parameter_ids = fields.One2many(
        comodel_name="law.analysis.parameter",
        inverse_name="analysis_id",
        string="Analysis Parameters"
    )

    _sql_constraints = [
        ('name_unique', 'unique(name)',
         'The client must be unique!'),
        ('coordinate_x_equal_greater_than_0',
         'CHECK(coordinate_x >= 0)',
         'The coordinate X must be equal or greater than 0!'),
        ('coordinate_y_equal_greater_than_0',
         'CHECK(coordinate_y >= 0)',
         'The coordinate Y must be equal or greater than 0!'),
        ('collection_time_before_receival_time',
         'CHECK(collection_time <= receival_time)',
         'The collection time must be after the receival time!'),
        ('analysis_start_time_before_analysis_end_time',
         'CHECK(analysis_start_time <= analysis_end_time)',
         'The analysis start time must be after the analysis end time!'),
    ]

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            if self.search([('name', '=', record.name),
                            ('id', '!=', record.id)]):
                raise ValidationError('The name must be unique!')

    @api.constrains('coordinate_x')
    def _check_coordinate_x(self):
        for record in self:
            if record.coordinate_x < 0:
                raise ValidationError(
                    'The coordinate X must be equal or greater than 0!')

    @api.constrains('coordinate_y')
    def _check_coordinate_y(self):
        for record in self:
            if record.coordinate_y < 0:
                raise ValidationError(
                    'The coordinate Y must be equal or greater than 0!')

    @api.constrains('collection_time', 'receival_time')
    def _check_collection_time_before_receival_time(self):
        for record in self:
            if record.collection_time and record.receival_time\
                    and record.collection_time > record.receival_time:
                raise ValidationError(
                    'The collection time must be before the receival time!')

    @api.constrains('analysis_start_time', 'analysis_end_time')
    def _check_analysis_start_time_before_analysis_end_time(self):
        for record in self:
            if record.analysis_start_time and record.analysis_end_time\
                    and record.analysis_start_time > record.analysis_end_time:
                raise ValidationError(
                    'The analysis start time must be before the analysis'
                    ' end time!')
