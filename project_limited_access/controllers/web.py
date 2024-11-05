# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.addons.portal.controllers.web import Home
from odoo.http import request


class HomeProjectLimited(Home):

    @http.route()
    def web_client(self, s_action=None, **kw):
        if (request.session.uid and
           not (request.env['res.users'].sudo().browse(
               request.session.uid).has_group(
                   'base.group_user') or
               request.env['res.users'].sudo().browse(
                   request.session.uid).has_group(
                       'project_limited_access.group_portal_project_user'))):
            return http.local_redirect('/my', query=request.params,
                                       keep_hash=True)
        return super(Home, self).web_client(s_action, **kw)

    @http.route(
        '/web/login', type='http', auth='public', website=True, csrf=False)
    def web_login(self, *args, **kw):
        response = super(HomeProjectLimited, self).web_login(*args, **kw)
        # If User created with user_type redirect to the config page
        if (request.httprequest.method == 'POST' and request.session.uid and
                request.env['res.users'].sudo().browse(
                    request.session.uid).has_group(
                    'project_limited_access.group_portal_project_user')):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash('/web')
        return response

    # Overwrite
    def _login_redirect(self, uid, redirect=None):
        """ Redirect regular users (employees) or group_portal_project_user to
        the backend) and others to the frontend
        """
        if not redirect and request.params.get('login_success'):
            if request.env['res.users'].browse(uid).has_group(
                'base.group_user') or request.env['res.users'].browse(
                    uid).has_group(
                        'project_limited_access.group_portal_project_user'):
                redirect = '/web?' + request.httprequest.query_string.decode()
            else:
                redirect = '/my'
        return super()._login_redirect(uid, redirect=redirect)