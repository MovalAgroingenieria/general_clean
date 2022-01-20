# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, exceptions, _


class BoardGrafana(models.Model):
    _name = 'board.grafana'
    _description = "Board Grafana"

    def _default_grafana_frame(self):
        grafana_url = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_url')
        grafana_user = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_user')
        grafana_pw = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_pw')
        grafana_org_id = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_org_id')
        if (not grafana_url or not grafana_user or not grafana_pw or not
                grafana_org_id):
            raise exceptions.ValidationError(
                _('The grafana configuration parameters have not been set.'))
        credentials = grafana_user + ':' + grafana_pw + '@'
        org_id = '?orgId=' + str(grafana_org_id)
        url_with_credentials = 'https://' + credentials + grafana_url + org_id
        frame_url = 'https://' + grafana_url + org_id
        frame_params = 'width="100%" height="800"'
        frame_layout = '<iframe id="grafana_frame" marginwidth="0" ' + \
            'marginheight="0" frameborder="no" style="display:none;" ' + \
            frame_params + ' src="' + url_with_credentials + '"></iframe>'
        script_js = '<script> setTimeout( () => {document.getElementById(' + \
            '"grafana_frame").src ="' + frame_url + '"}, 500); ' + \
            'setTimeout( () => {document.getElementById(' + \
            '"grafana_frame").style = "unset"}, 1000);</script>'
        grafana_frame = frame_layout + script_js
        return grafana_frame

    grafana_frame = fields.Text(
        string='Grafana frame',
        default=_default_grafana_frame,
        compute='_compute_grafana_frame')

    @api.multi
    def _compute_grafana_frame(self):
        self.grafana_frame = False

    @api.multi
    def action_go_to_grafana_server(self):
        grafana_url = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_url')
        grafana_user = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_user')
        grafana_pw = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_pw')
        grafana_org_id = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_org_id')
        if (not grafana_url or not grafana_user or not grafana_pw or not
                grafana_org_id):
            raise exceptions.ValidationError(
                _('The grafana configuration parameters have not been set.'))
        org_id = '?orgId=' + str(grafana_org_id)
        server_url = 'https://' + grafana_url + org_id
        return {
            'type': 'ir.actions.act_url',
            'url': server_url,
            'target': 'new',
        }

    def create_grafana_frame(self, frame_src, frame_params):
        grafana_url = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_url')
        grafana_user = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_user')
        grafana_pw = self.env['ir.values'].get_default(
            'board.grafana.configuration', 'grafana_pw')
        if (not grafana_url or not grafana_user or not grafana_pw):
            raise exceptions.ValidationError(
                _('The grafana configuration parameters have not been set.'))
        credentials = grafana_user + ':' + grafana_pw + '@'
        frame_with_credentials = \
            'https://' + credentials + grafana_url + frame_src
        frame_url = 'https://' + grafana_url + frame_src
        frame_layout = '<iframe id="grafana_frame" marginwidth="0" ' + \
            'marginheight="0" frameborder="no" style="display:none;" ' + \
            frame_params + ' src="' + frame_with_credentials + '"></iframe>'
        script_js = '<script> setTimeout( () => {document.getElementById(' + \
            '"grafana_frame").src ="' + frame_url + '"}, 500); ' + \
            'setTimeout( () => {document.getElementById(' + \
            '"grafana_frame").style = "unset"}, 1000);</script>'
        grafana_frame = frame_layout + script_js
        return grafana_frame
