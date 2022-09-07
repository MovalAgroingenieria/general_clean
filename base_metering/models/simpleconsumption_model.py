# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, exceptions, _


class SimpleconsumptionModel(models.AbstractModel):
    _name = 'simpleconsumption.model'
    _description = 'Simple model for consumptions of water'
    _order = 'name'

    # Size of "name" field, in the model.
    MAX_SIZE_NAME_FIELD = 52

    reading_ids = fields.One2many(
        string='Readings',
        comodel_name='simplereading.model',
        inverse_name='consumption_id',)

    reading_id = fields.Many2one(
        string='Reading',
        comodel_name='simplereading.model',
        ondelete='cascade',
        store=True,
        compute='_compute_reading_id',)

    initial_time = fields.Datetime(
        string='Initial Time',
        required=True,
        readonly=True,
        default=lambda self: fields.datetime.now(),)

    final_time = fields.Datetime(
        string='Final Time',
        store=True,
        default=lambda self: fields.datetime.now(),
        compute='_compute_final_time',
        index=True,)

    duration = fields.Integer(
        string='Duration (s)',
        store=True,
        compute='_compute_duration',
        index=True,)

    initial_volume = fields.Float(
        string='Initial Volume (m³)',
        digits=(32, 2),
        required=True,
        readonly=True,
        default=0,)

    final_volume = fields.Float(
        string='Final Volume (m³)',
        store=True,
        compute='_compute_final_volume',
        default=0,)

    raw_volume = fields.Float(
        string='Raw Volume (m³)',
        store=True,
        compute='_compute_raw_volume',
        index=True,
        default=0,)

    adjustement = fields.Float(
        string='Adjust. (m³)',
        required=True,
        digits=(32, 2),
        default=0,
        index=True,)

    volume = fields.Float(
        string='Volume (m³)',
        store=True,
        compute='_compute_volume',
        index=True)

    validated = fields.Boolean(
        string='Validated Consumption',
        store=True,
        compute='_compute_validated',)

    meter_id = fields.Many2one(
        string='Meter',
        comodel_name='auxiliary.meter',
        ondelete='restrict',
        store=True,
        compute='_compute_meter_id',)

    name = fields.Char(
        string='Consumption Identifier',
        size=MAX_SIZE_NAME_FIELD,
        store=True,
        compute='_compute_name',
        index=True,)

    notes = fields.Html(
        string="Notes",
        help="Notes about reading",)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE (name)',
         'Existing Code.'),
        ('correct_times',
         'CHECK (validated = false or final_time > initial_time)',
         'The final time must be greather than the initial time.'),
        ('correct_raw_volume',
         'CHECK (raw_volume >= 0)',
         'Raw volume can\'t be negative.'),
        ]

    @api.depends('reading_ids')
    def _compute_reading_id(self):
        for record in self:
            reading_id = None
            if record.reading_ids:
                reading_id = record.reading_ids[0]
            record.reading_id = reading_id

    @api.depends('reading_id', 'reading_id.reading_time')
    def _compute_final_time(self):
        for record in self:
            final_time = None
            if record.reading_id:
                final_time = record.reading_id.reading_time
            record.final_time = final_time

    @api.depends('initial_time', 'final_time')
    def _compute_duration(self):
        for record in self:
            duration = 0
            if record.initial_time and record.final_time:
                initial_time = record.initial_time
                final_time = record.final_time
                duration = (final_time - initial_time).total_seconds()
            record.duration = duration

    @api.depends('reading_id', 'reading_id.volume')
    def _compute_final_volume(self):
        for record in self:
            final_volume = 0
            if record.reading_id:
                final_volume = record.reading_id.volume
            record.final_volume = final_volume

    @api.depends('initial_volume', 'final_volume')
    def _compute_raw_volume(self):
        for record in self:
            raw_volume = record.final_volume - record.initial_volume
            record.raw_volume = raw_volume

    @api.depends('raw_volume', 'adjustement')
    def _compute_volume(self):
        for record in self:
            volume = record.raw_volume + record.adjustement
            record.volume = volume

    @api.depends('reading_id', 'reading_id.validated')
    def _compute_validated(self):
        for record in self:
            validated = False
            if record.reading_id and record.reading_id.validated:
                validated = True
            record.validated = validated

    @api.depends('reading_id', 'reading_id.meter_id')
    def _compute_meter_id(self):
        for record in self:
            meter_id = None
            if record.reading_id and record.reading_id.meter_id:
                meter_id = record.reading_id.meter_id
            record.meter_id = meter_id

    @api.depends('final_time', 'meter_id')
    def _compute_name(self):
        for record in self:
            name = record.final_time
            if record.meter_id:
                name = record.meter_id.name + '-' + name
            record.name = name

    @api.constrains('reading_ids')
    def _check_reading_ids(self):
        for record in self:
            if record.reading_ids and len(record.reading_ids > 1):
                raise exceptions.ValidationError(_(
                    'Only one final reading is allowed for one consumption.'))
