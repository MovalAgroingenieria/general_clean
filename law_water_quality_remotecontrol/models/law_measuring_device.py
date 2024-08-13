# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import models, api, fields, _, exceptions


class LawMeasuringDevice(models.Model):
    _inherit = 'law.measuring.device'

    def _get_default_remotecontrol_measurement_transformation(self):
        transformation = '$'
        if (self.measuring_device_type_id):
            transformation = self.measuring_device_type_id.\
                remotecontrol_measurement_transformation
        return transformation

    # Empty, inherit
    telecontrol_associated = fields.Selection(
        [],
        string='Type of telecontrol associated',
    )

    remotecontrol_enabled = fields.Boolean(
        string='Remote Control enabled',
        compute='_compute_remotecontrol_enabled',
    )

    remotecontrol_measurement_transformation = fields.Char(
        string='Measurement Transformation',
        required=True,
        default=_get_default_remotecontrol_measurement_transformation,
        help='Transformation to apply to the measurement value before saving '
             '. Use $ as placeholder for the original raw value.',
    )

    @api.onchange('measuring_device_type_id')
    def _onchange_measuring_device_type_id(self):
        self.remotecontrol_measurement_transformation = \
            self._get_default_remotecontrol_measurement_transformation()

    @api.multi
    def _compute_remotecontrol_enabled(self):
        remotecontrol_enabled = self.env['ir.values'].get_default(
            'law.measuring.configuration', 'remotecontrol_enabled')
        if remotecontrol_enabled is None:
            remotecontrol_enabled = False
        self.write({'remotecontrol_enabled': remotecontrol_enabled})

    @api.multi
    def do_import_measurements_from_measuring_device(self):
        self.ensure_one()
        prefix_message = _('Remote Control: Starting import measurement '
                           'in measuremente devices')
        _logger = logging.getLogger(self.__class__.__name__)
        _logger.info(prefix_message + '... ' +
                     str(self.name))
        self.env['law.measuring.device.measurement'].\
            do_import_measurements(save_data=True, show_message=True,
                                   device_ids=[self.id])

    def do_import_measurements_from_measuring_devices(
            self, active_measuring_devices):
        if (not self.env.user.has_group('law_water_quality.'
                                        'group_law_manager')):
            raise exceptions.UserError(_(
                'You do not have permission to execute this action.'))
        measuring_devices = self.env['law.measuring.device'].browse(
            active_measuring_devices)
        if measuring_devices:
            prefix_message = _('Remote Control: Starting reading in '
                               'measuring devices')
            suffix_message = ''
            for measuring_device in measuring_devices:
                suffix_message = suffix_message + ', ' + measuring_device.name
            suffix_message = suffix_message[2:]
            _logger = logging.getLogger(self.__class__.__name__)
            _logger.info(prefix_message + '... ' + suffix_message)
            self.env['law.measuring.device.measurement'].\
                do_import_measurements(save_data=True, show_message=True,
                                       device_ids=active_measuring_devices)
