# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import datetime
import pytz
from odoo import models, fields, api, exceptions, _


class AuxiliaryMeter(models.AbstractModel):
    _name = 'auxiliary.meter'
    _description = 'Auxiliar class to considerer abstract meters'

    name = fields.Char(
        string='Meter Identifier',)

    is_active = fields.Boolean(
        string='Active',)


class SimplereadingModel(models.AbstractModel):
    _name = 'simplereading.model'
    _description = 'Simple model for readings linked to consumptions'
    _order = 'name'

    _reading_table = ''

    # Size of "name" field, in the model.
    MAX_SIZE_NAME_FIELD = 52

    meter_id = fields.Many2one(
        string='Meter',
        comodel_name='auxiliary.meter',
        required=True,
        ondelete='restrict',
        index=True,
        domain=[('is_active', '=', True)],)

    reading_time = fields.Datetime(
        string='Time',
        required=True,
        index=True,
        default=lambda self: fields.datetime.now(),)

    name = fields.Char(
        string='Reading Identifier',
        size=MAX_SIZE_NAME_FIELD,
        store=True,
        compute='_compute_name',
        index=True,)

    initialization_reading = fields.Boolean(
        string='Initialization Reading',
        required=True,
        default=False,)

    volume = fields.Float(
        string='Volume (m³)',
        digits=(32, 2),
        required=True,
        default=0,)

    consumption_id = fields.Many2one(
        string='Consumption',
        comodel_name='simpleconsumption.model',
        ondelete='restrict',
        readonly=True,)

    validated = fields.Boolean(
        string='Validated Reading',
        default=True,
        required=True,)

    is_last_reading = fields.Boolean(
        string='Last Reading',
        compute='_compute_is_last_reading',)

    notes = fields.Html(
        string="Notes",
        help="Notes about reading",)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE (name)',
         'Existing Code.'),
        ('volume',
         'CHECK (volume >= 0)',
         'Volume of water can\'t be negative.'),
        ]

    @api.depends('reading_time', 'meter_id')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.meter_id and record.reading_time:
                name = record.meter_id.name + '-' + str(record.reading_time)
            record.name = name

    def _compute_is_last_reading(self):
        for record in self:
            is_last_reading = False
            if record.meter_id:
                sql = 'SELECT count(*) FROM ' + self._reading_table + \
                      ' WHERE meter_id = ' + str(record.meter_id.id) + \
                      ' AND reading_time > \'' + str(record.reading_time) + \
                      '\''
                self.env.cr.execute(sql)
                query_results = self.env.cr.dictfetchall()
                number_later_readings = query_results[0].get('count')
                if number_later_readings == 0:
                    is_last_reading = True
            record.is_last_reading = is_last_reading

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Main fields.
            reading_time = vals['reading_time']
            volume = vals['volume']
            # Data to create the consumption.
            consumption_initial_time = None
            consumption_initial_volume = 0
            # Meter and other entries of vals.
            meter_id = vals['meter_id']
            meter = self._get_meter(meter_id)
            vals_ok = self._get_additional_vals(vals, meter)
            if ((not meter) or (not vals_ok)):
                vals = {}
                continue
            is_initialization_reading = vals['initialization_reading']
            if not is_initialization_reading:
                # Create the consumption, 1/2: the new reading must be the last
                # reading.
                sql = 'SELECT count(*) FROM ' + self._reading_table + \
                      ' WHERE meter_id = ' + str(meter_id) + \
                      ' AND reading_time > \'' + str(reading_time) + '\''
                self.env.cr.execute(sql)
                query_results = self.env.cr.dictfetchall()
                number_later_readings = query_results[0].get('count')
                if number_later_readings > 0:
                    raise exceptions.UserError(_('There are readings after '
                                                 'the new reading.'))
                # Create the consumption, 2/2: create the record.
                sql = 'SELECT reading_time, volume FROM ' + \
                      self._reading_table + \
                      ' WHERE meter_id = ' + str(meter_id) + \
                      ' ORDER BY reading_time DESC LIMIT 1'
                self.env.cr.execute(sql)
                query_results = self.env.cr.dictfetchall()
                if query_results:
                    consumption_initial_time = \
                        query_results[0].get('reading_time')
                    consumption_initial_volume = query_results[0].get('volume')
                    # Important: The final values are calculated values in the
                    # consumptions model.
                    new_consumption = self._create_consumption(
                        consumption_initial_time, consumption_initial_volume)
                    vals['consumption_id'] = new_consumption.id
                else:
                    vals['initialization_reading'] = True
        vals_list = list(filter(None, vals_list))
        new_readings = self._create_readings(vals_list)
        return new_readings

    def write(self, vals):
        resp = self._write_readings(vals)
        if 'meter_id' in vals or 'reading_time' in vals:
            raise exceptions.UserError(_('It is not possible to change the '
                                         'meter or time of a reading.'))
        return resp

    def unlink(self):
        if not self.env.context.get('force_unlink', False):
            detected_not_last_reading = False
            for record in self:
                if not record.is_last_reading:
                    detected_not_last_reading = True
                    break
            if detected_not_last_reading:
                raise exceptions.UserError(_('There can be no final readings '
                                             'without eliminating.'))
        return self._unlink_readings()

    def name_get(self):
        result = []
        for record in self:
            meter_name = record.meter_id.name
            reading_time = \
                fields.Datetime.from_string(record.reading_time)
            if self.env.user.tz:
                local_timezone = pytz.timezone(self.env.user.tz)
                offset = local_timezone.utcoffset(reading_time)
                reading_time = reading_time + offset
            reading_time_str = str(reading_time)
            date_str = reading_time_str[:10]
            hour_str = reading_time_str[-8:]
            name = meter_name + ' - ' + \
                datetime.datetime.strptime(
                    date_str, '%Y-%m-%d').strftime('%x') + ' ' + hour_str
            result.append((record.id, name))
        return result

    def action_validate_reading(self):
        for record in self:
            if not record.validated:
                record.validated = True

    def action_cancel_reading(self):
        for record in self:
            if record.validated:
                record.validated = False

    # Hook
    def _get_meter(self, meter_id):
        return None

    # Hook
    def _get_additional_vals(self, vals, meter):
        return True

    # Hook
    def _create_readings(self, vals):
        return super(SimplereadingModel, self).create(vals)

    # Hook
    def _write_readings(self, vals):
        return super(SimplereadingModel, self).write(vals)

    # Hook
    def _unlink_readings(self):
        return super(SimplereadingModel, self).unlink()

    # Hook
    def _create_consumption(self, initial_time, initial_volume):
        return None
