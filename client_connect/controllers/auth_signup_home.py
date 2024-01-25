# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home


class CustomSessionController(Home):

    @http.route('/web/login', type='http', auth='none', website=True)
    def web_login(self, redirect=None, **kw):
        response = super(CustomSessionController, self).web_login(
            redirect=redirect, **kw)

        countries = request.env['res.country'].sudo().search([])
        response.qcontext['countries'] = countries

        lang_list = request.env['res.lang'].sudo().search([])
        response.qcontext['lang_list'] = lang_list

        # If the login was successful
        if request.httprequest.method == 'POST' and request.session.uid:
            login_info = {
                'database': request.db,
                'mail': kw.get('mail'),
                'phone': kw.get('phone'),
                'company': kw.get('company'),
                'country': kw.get('country'),
            }
            request.env['client_connect'].sudo().create(login_info)

        return response
