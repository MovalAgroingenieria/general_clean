# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class OmaConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'oma.configuration'
    _description = 'Firebase Cloud Messaging Configuration'

    firebase_credentials = fields.Binary(
        string='Firebase Credentials',
        required=True,
    )

    firebase_credentials_filename = fields.Char(
        string='Firebase Credentials Filename',
        default='credentials.json',
    )

    firebase_project_id = fields.Char(
        string='Firebase Project ID',
        required=True,
    )
    fcm_endpoint = fields.Char(
        string='FCM Endpoint',
    )

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('oma.configuration',
                           'firebase_credentials', self.firebase_credentials)
        values.set_default('oma.configuration',
                           'firebase_credentials_filename',
                           'credentials.json')
        values.set_default('oma.configuration',
                           'firebase_project_id', self.firebase_project_id)
        values.set_default('oma.configuration',
                           'fcm_endpoint', self.fcm_endpoint)
