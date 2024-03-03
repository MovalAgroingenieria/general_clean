# -*- coding: utf-8 -*-
# Copyright 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import http, _
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteFormCim(WebsiteForm):

    @http.route()
    def website_form(self, model_name, **kwargs):
        value_to_return = super(WebsiteFormCim, self).website_form(
            model_name, **kwargs)
        if model_name == 'cim.complaint':
            new_id = 0
            new_tracking_code = ''
            response = value_to_return.response
            if response:
                try:
                    response = json.loads(response[0])
                    if 'id' in response and response['id']:
                        new_id = response['id']
                        complaint = request.env['cim.complaint'].sudo().browse(
                            new_id)
                        if complaint:
                            new_tracking_code = \
                                complaint.decrypted_tracking_code
                except Exception:
                    new_id = 0
                    new_tracking_code = ''
            if new_id and new_tracking_code:
                value_to_return = {
                    'id': new_id,
                    'tracking_code_new_complaint': new_tracking_code, }
                value_to_return = json.dumps(value_to_return)
            else:
                value_to_return = json.dumps(False)
        return value_to_return

    def insert_record(self, request, model, values, custom, meta=None):
        if model.model == 'cim.complaint':
            values['complaint_lang'] = request.httprequest.cookies.get(
                'website_lang')
        return super(WebsiteFormCim, self).insert_record(
            request, model, values, custom, meta)

    @http.route('/tracking-code', type='http', auth='public',
                website=True)
    def show_tracking_code(self, **kwargs):
        tracking_code = 0
        if request.httprequest.method == 'GET':
            tracking_code = request.params.get('code')
        text_to_show = _('(code not available)')
        if tracking_code:
            text_to_show = tracking_code
        return request.render(
            'cim_complaints_channel.trackingcode_page',
            {'tracking_code': text_to_show})
