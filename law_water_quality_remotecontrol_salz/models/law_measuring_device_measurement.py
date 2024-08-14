# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import hashlib
import json
import requests
from odoo import models, api, exceptions, _


class LawMeasuringDeviceMeasurement(models.Model):
    _inherit = 'law.measuring.device.measurement'

    @api.model
    def run_remotecontrol_application_url_salz(self):
        remotecontrol_enabled = self.env['ir.values'].get_default(
            'law.measuring.configuration', 'remotecontrol_enabled')
        if not remotecontrol_enabled:
            raise exceptions.UserError(_('The remote control is not enabled.'))
        url_remote_app_salz = self.env['ir.values'].get_default(
            'law.measuring.configuration',
            'url_remote_app_salz')
        if not url_remote_app_salz:
            raise exceptions.UserError(_('There is not a URL for the '
                                         'remote control application.'))
        return {
            'type': 'ir.actions.act_url',
            'url': url_remote_app_salz,
            'target': 'new', }

    def _get_connection_parameters_salz(self):
        url_remotecontrol_rest = self.env['ir.values'].get_default(
            'law.measuring.configuration', 'url_remote_api_rest_salz')
        url_remotecontrol_rest_username = self.env['ir.values'].\
            get_default('law.measuring.configuration',
                        'url_remote_api_rest_username_salz')
        url_remotecontrol_rest_password = self.env['ir.values'].\
            get_default('law.measuring.configuration',
                        'url_remote_api_rest_password_salz')
        if (url_remotecontrol_rest_password):
            url_remotecontrol_rest_password = hashlib.md5(
                url_remotecontrol_rest_password).hexdigest()
        return url_remotecontrol_rest, url_remotecontrol_rest_username, \
            url_remotecontrol_rest_password

    def _get_measurement_value_of_device(self, device_id, measurement):
        value = None
        if (device_id.salz_plate_number and device_id.salz_measure_variable):
            plate = measurement[device_id.salz_plate_number - 1]
            for variable in plate['variablesplaca']:
                if (variable['descripcion'] ==
                        device_id.salz_measure_variable):
                    value = variable['valor']
                    break
        return value

    def populate_data_for_import_measurements_salz(
            self, url_remotecontrol_rest, url_remotecontrol_rest_username,
            url_remotecontrol_rest_password, device_ids):
        # Get all active measuring device that are associated with Salz for
        # later usage
        resp = []
        search_domain = [
            ('telecontrol_associated', '=', 'salz'),
            ('salz_device_id', '>', 0),
            ('salz_device_gid', '>', 0),
        ]
        if (device_ids and len(device_ids) > 0):
            search_domain.append(('id', 'in', device_ids))
        resp = self.env['law.measuring.device'].search(search_domain)
        return resp

    def import_measurements_salz(
            self,
            url_remotecontrol_rest, url_remotecontrol_rest_username,
            url_remotecontrol_rest_password, device_ids):
        measurements = []
        error_message = ''
        error_measuring_devices = []
        for device in device_ids:
            post_data = {
                'idgrupo': device.salz_device_gid,
                'idpropio': device.salz_device_id,
                'idusuario': 0,
                'password': url_remotecontrol_rest_password,
                'usuario': url_remotecontrol_rest_username, }
            headers_data = {'content-type': 'application/json', }
            res_raw = requests.post(
                url_remotecontrol_rest, data=json.dumps(post_data),
                headers=headers_data)
            if res_raw:
                res_json = json.loads(res_raw.content)
                if (res_json and 'respuesta' in res_json and
                        res_json['respuesta']['codigo'] == 'OK'):
                    # Get value of measurement
                    value = self._get_measurement_value_of_device(
                        device, res_json['placas'])
                    # Value can be 0 and that's ok
                    if (value is not None):
                        measurements.append({
                            'measuring_device_id': device,
                            'value': value,
                        })
                elif (res_json and 'respuesta' in res_json and
                      res_json['respuesta']['codigo'] == 'ERROR'):
                    # Controlled error
                    error_message += '. ' + res_json['respuesta']['mensaje']
                    error_measuring_devices.append(device.name)
                else:
                    # Uncontrolled error
                    error_message += _(
                        ' It is not possible to get a response. ')
                    error_measuring_devices.append(device.name)
        return [measurements, error_message, error_measuring_devices]

    # Hook that will be implemeneted on every telecontrol, appending the info
    def do_import_measurement_of_telecontrol(self, device_ids=[]):
        # Get super data and then append here data
        # Result in format [measurements, error_message,
        #                   error_measuring_devices]
        others_measurements_info = \
            list(super(LawMeasuringDeviceMeasurement, self).
                 do_import_measurement_of_telecontrol(device_ids))
        url_remotecontrol_rest, url_remotecontrol_rest_username, \
            url_remotecontrol_rest_password = self.\
            _get_connection_parameters_salz()
        if (url_remotecontrol_rest and url_remotecontrol_rest_username and
                url_remotecontrol_rest_password):
            try:
                data = self.populate_data_for_import_measurements_salz(
                    url_remotecontrol_rest,
                    url_remotecontrol_rest_username,
                    url_remotecontrol_rest_password,
                    device_ids)
                if data and len(data) > 0:
                    measurements, error_message, error_measuring_devices = \
                        self.import_measurements_salz(
                            url_remotecontrol_rest,
                            url_remotecontrol_rest_username,
                            url_remotecontrol_rest_password, data)
                    if (measurements):
                        # Merge arrays
                        others_measurements_info[0] += measurements
                    if (error_message):
                        # Merge Strings
                        others_measurements_info[1] += ' - ' + error_message
                    if (error_measuring_devices):
                        # Merge Strings
                        others_measurements_info[2] += error_measuring_devices
            except Exception as e:
                others_measurements_info[1] += ' - ' + 'SALZ error:\n\n' + \
                    str(e) + '\n\n'
        return others_measurements_info
