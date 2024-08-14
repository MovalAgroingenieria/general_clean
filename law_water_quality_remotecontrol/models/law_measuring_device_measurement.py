# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, api, fields, exceptions, _


class LawMeasuringDeviceMeasurement(models.Model):
    _inherit = 'law.measuring.device.measurement'

    from_remotecontrol = fields.Boolean(
        string='From Remote Control',
        default=False,
        required=True,
    )

    raw_remotecontrol_value = fields.Float(
        string='Raw Remote Control Value',
        digits=(32, 4),
    )

    # Hook that will be implemeneted on every telecontrol, appending the info
    def do_import_measurement_of_telecontrol(self, device_ids=[]):
        measurements = []
        error_message = ''
        error_devices = []
        return measurements, error_message, error_devices

    @api.model
    def do_import_measurements(self, save_data=True, show_message=True,
                               device_ids=[]):
        # for resp: item 1: list of measurements, item 2: number of
        # measurements, item 3: possible error message,
        # item 4: list of problematic devices
        resp = [None, 0, '', None, 0]
        remotecontrol_enabled = self.env['ir.values'].get_default(
            'law.measuring.configuration', 'remotecontrol_enabled')
        if (remotecontrol_enabled):
            # GET MEASURMENTS OF ALL POSSIBLE TELECONTROLS AND THEN
            # UPDATE IT
            measurements, error_message, error_watermeters = \
                self.do_import_measurement_of_telecontrol(device_ids)
            measurements = self.refine_measurements(measurements)
            if measurements:
                resp[0] = measurements
                resp[1] = len(measurements)
                resp[2] = error_message
                resp[3] = error_watermeters
                if save_data:
                    self.save_measurements(measurements)
                prefix_message_01 = _('Remote Control: '
                                      'Getting measurements')
                suffix_message_01 = str(resp[1])
                _logger = logging.getLogger(self.__class__.__name__)
                _logger.info(prefix_message_01 + '... ' +
                             suffix_message_01)
            if error_message:
                prefix_message_02 = _('Remote Control: '
                                      'Error getting measurements')
                suffix_message_02 = resp[2]
                company_name = self.env.user.company_id.name
                website_url = self.env['ir.config_parameter'].get_param(
                    "web.base.url")
                domain = self.env['ir.config_parameter'].get_param(
                    "mail.catchall.domain")
                _logger = logging.getLogger(
                    self.__class__.__name__)
                _logger.info(prefix_message_02 + '... ' +
                             suffix_message_02)
                telecontrol_failed_template_id = self.env.ref(
                    'law_water_quality_remotecontrol.'
                    'telecontrol_failed_email_template').id
                mail_template = self.env['mail.template'].browse(
                    telecontrol_failed_template_id)
                mail_template.subject = '''
                    Measurement remote control in %s has
                    experienced some problem
                ''' % (domain or self.pool.db_name)
                mail_template.body_html = '''
                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                        <b><a href="%s">%s</a></p></b>
                        <br/>
                        <span>%s</span>
                    </p>
                ''' % (website_url, company_name, resp[2].replace(
                    '\n', '<br/>'))
                mail_template.send_mail(self.id, force_send=True)
        else:
            if show_message:
                raise exceptions.UserError(_('The communication with '
                                             'the remote control is not '
                                             'enabled.'))
        return resp

    # Hook
    def get_measurement_time(self, measurement):
        return fields.Datetime.now()

    def transform_measurement_value(self, value, transformation):
        # Replace the placeholder with the value
        # TODO: Add checks before eval to avoid execution of malicious code
        return eval(transformation.replace('$', str(value)))

    def refine_measurements(self, measurements):
        resp = []
        for measurement in measurements:
            device = measurement['measuring_device_id']
            # If not specified measurement time will be the current one
            measurement_time = self.get_measurement_time(measurement)
            # Transform the value
            measurement_value = self.transform_measurement_value(
                measurement['value'],
                device.remotecontrol_measurement_transformation)
            # Set refined data
            refined_measurement = {
                'measuring_device_id': device.id,
                'measurement_time': measurement_time,
                'device_name': device.name,
                'value': measurement_value,
                'uom_id': device.uom_id.id,
                'raw_remotecontrol_value': str(measurement['value']),
                }
            resp.append(refined_measurement)
        return resp

    def save_measurements(self, measurements, update_log=True):
        number_of_measurements = len(measurements)
        if number_of_measurements > 0:
            for measurement in measurements:
                self.create({
                    'measuring_device_id': measurement[
                        'measuring_device_id'],
                    'measurement_time': measurement['measurement_time'],
                    'value': measurement['value'],
                    'raw_remotecontrol_value': measurement[
                        'raw_remotecontrol_value'],
                    'uom_id': measurement['uom_id'],
                    'from_remotecontrol': True,
                    })
            if update_log:
                _logger = logging.getLogger(self.__class__.__name__)
                _logger.info(_('Remote Control: Saved measurements') + '... ' +
                             str(number_of_measurements))
