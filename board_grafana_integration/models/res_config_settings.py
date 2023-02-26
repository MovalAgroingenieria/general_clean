# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api

class BoardGrafanaConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Configuration of Grafana'

    DEFAULT_DASHBOARD_HEIGHT = 800

    grafana_url_raw = fields.Char(
        string='URL',
        config_parameter='board_grafana_integration.grafana_url_raw',
        help='The URL of grafana host.',)

    grafana_url = fields.Char(
        compute="_compute_grafana_url",
        config_parameter='board_grafana_integration.grafana_url',)

    grafana_dashboard_height = fields.Integer(
        string='Height',
        config_parameter='board_grafana_integration.grafana_dashboard_height',
        help='Height of dashboard, in pixels (optional).',)

    grafana_dashboard_id = fields.Char(
        string='Id',
        config_parameter='board_grafana_integration.grafana_dashboard_idt',
        help='The id of the embebbed dashboard '
             '(optional, else the default dashboard).')

    @api.depends('grafana_url_raw')
    def _compute_grafana_url(self):
        for record in self:
            url = record.grafana_url_raw
            if url.endswith('/'):
                url = url.rstrip('/')
            record.grafana_url = url

    @api.depends('grafana_url')
    def action_go_to_grafana_server(self):
        grafana_url = self.grafana_url
        if self.grafana_dashboard_id:
            grafana_url = grafana_url + '/d/' + self.grafana_dashboard_id
        return {
            'type': 'ir.actions.act_url',
            'url': grafana_url,
        }
