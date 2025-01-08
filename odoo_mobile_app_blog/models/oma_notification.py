# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import json


class Notification(models.Model):
    _inherit = 'oma.notification'

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

    @api.multi
    def action_send(self):
        self.write({'state': '03_sending'})
        for record in self:
            token = record.token_id.name
            title = record.title
            subtitle = record.subtitle
            body = record.body
            url_img = record.url_img if record.url_img else ''
            url_notification = record.url_notification \
                if record.url_notification else ''
            notification_id = record.id
            post_id = record.post_id.id if record.post_id else False
            try:
                resp = self.env['oma.notification.set']._send_notification(
                    token, title, subtitle, body, url_img, url_notification,
                    notification_id, post_id)
                if resp.status_code == 200:
                    self.env['oma.notification.event'].create({
                        'notification_id': record.id,
                        'event_type': 'send',
                        'event_message': resp.text,
                    })
                    record.write({'state': '04_sent'})
                else:
                    self.env['oma.notification.event'].create({
                        'notification_id': record.id,
                        'event_type': 'error',
                        'event_message': resp.text,
                    })
                    record.write({'state': '99_error'})
            except Exception as e:
                self.env['oma.notification.event'].create({
                    'notification_id': record.id,
                    'event_type': 'error',
                    'event_message': str(e),
                })
                record.write({'state': '99_error'})
