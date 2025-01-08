# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import requests
import json


class OmaNotificationSet(models.Model):
    _inherit = 'oma.notification.set'

    post_id = fields.Many2one(
        comodel_name='blog.post',
        string="Related Blog Post",
        domain=[('website_published', '=', True)],
        help="Select a related blog post."
    )

    @api.onchange('post_id')
    def _onchange_post_id(self):
        base_web_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        if self.post_id:
            self.title = self.post_id.name
            self.subtitle = self.post_id.subtitle
            self.body = self.post_id.content
            self.url_img = base_web_url + \
                json.loads(self.post_id.cover_properties)['background-image']\
                    .replace('url(', '').replace(')', '')
        else:
            self.title = False
            self.subtitle = False
            self.body = False
            self.url_img = False

    def _send_notification(
        self, token, title, subtitle, body, url_img, url_notification,
            notification_id, post_id):
        headers = {
            'Authorization': 'Bearer ' + self._get_access_token(),
            'Content-Type': 'application/json; UTF-8',
        }
        project_id = self.env['ir.values'].sudo().get_default(
            'oma.configuration', 'firebase_project_id')
        endpoint = 'https://fcm.googleapis.com/v1/projects/{}/messages:send'.\
            format(project_id)
        notification_data = {
            'url_img': url_img,
            'url_notification': url_notification,
            'notification_id': str(notification_id),
        }

        if post_id:
            notification_data['post_id'] = str(post_id)
        else:
            notification_data['html_body'] = body
        data = {
            'message': {
                'notification': {
                    'title': title,
                    'body': subtitle,
                },
                'data': notification_data,
                'token': token,
            }
        }
        resp = requests.post(endpoint, data=json.dumps(data), headers=headers)
        return resp
