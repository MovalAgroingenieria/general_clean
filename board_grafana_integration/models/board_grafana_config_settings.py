# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class BoardGrafanaConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'board.grafana.configuration'

    grafana_url_raw = fields.Char(
        string='Grafana URL',
        required=True,
        help='The URL of grafana host.')

    grafana_url = fields.Char(
        compute="_compute_grafana_url")

    grafana_user = fields.Char(
        string='Grafana user',
        required=True)

    grafana_pw = fields.Char(
        string='Grafana password',
        required=True,)

    grafana_org_id = fields.Integer(
        string='Organization id',
        required=True,
        help='The id of the organization.')

    @api.depends('grafana_url_raw')
    def _compute_grafana_url(self):
        for record in self:
            url = record.grafana_url_raw
            if url.startswith('http'):
                url_raw = url.split(':')[1]
                url = url_raw.replace('/', '')
            if url.endswith('/'):
                url = url.rstrip('/')
            record.grafana_url = url

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('board.grafana.configuration',
                           'grafana_url_raw', self.grafana_url_raw)
        values.set_default('board.grafana.configuration',
                           'grafana_url', self.grafana_url)
        values.set_default('board.grafana.configuration',
                           'grafana_user', self.grafana_user)
        values.set_default('board.grafana.configuration',
                           'grafana_pw', self.grafana_pw)
        values.set_default('board.grafana.configuration',
                           'grafana_org_id', self.grafana_org_id)
