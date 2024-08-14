# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class LawMeasuringDevice(models.Model):
    _inherit = 'law.measuring.device'

    telecontrol_associated = fields.Selection(
        selection_add=[('salz', 'Salz')])

    salz_device_id = fields.Integer(
        string='Salz Device ID',
        help='The id that identifies the remote Salz measuring device',
    )

    salz_device_gid = fields.Integer(
        string='Salz Device GID',
        help='The id that identifies the group of the remote Salz measuring '
             'device',
    )

    salz_plate_number = fields.Integer(
        string='Salz Plate Number',
        default=1,
        help='The plate number that stores the measure variable of the remote '
             'Salz measuring device',
    )

    salz_measure_variable = fields.Char(
        string='Salz Measure Variable',
        help='The id that identifies the measure variable of the remote Salz '
             'measuring device (description on remote)',
    )

    _sql_constraints = [
        ('negative_salz_device_id',
         'CHECK (salz_device_id >= 0)',
         'Salz Device ID can not be negative.'),
        ('negative_salz_device_gid',
         'CHECK (salz_device_id >= 0)',
         'Salz Device GID can not be negative.'),
        ('negative_salz_plate_number',
         'CHECK (salz_plate_number >= 0)',
         'Salz plate number can not be negative.'),
    ]
