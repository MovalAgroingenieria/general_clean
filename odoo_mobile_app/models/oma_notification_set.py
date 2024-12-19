# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from google.oauth2 import service_account
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import google.auth.transport.requests
import requests
import json
import base64
import logging
_logger = logging.getLogger(__name__)


class OmaNotificationSet(models.Model):
    _name = 'oma.notification.set'
    _description = 'Notification Set'

    name = fields.Char(
        string='Notification Identifier',
        required=True,
    )
    title = fields.Char(
        string='Title',
        required=True,
    )
    subtitle = fields.Char(
        string='Subtitle',
        required=True,
    )
    body = fields.Html(
        string='Content',
        required=True,
    )
    url_img = fields.Char(
        string='Image URL',
    )
    url_notification = fields.Char(
        string='Notification URL',
    )
    send_date = fields.Datetime(
        string='Send Date',
    )

    notification_ids = fields.One2many(
        string='Notifications',
        comodel_name='oma.notification',
        inverse_name='notificationset_id',
    )

    token_ids = fields.Many2many(
        string='Device Tokens',
        comodel_name='oma.token',
        default=lambda self: self.env['oma.token'].search([]).ids,
    )
    state = fields.Selection(
        selection=[
            ('01_draft', 'Draft'),
            ('02_prepared', 'Prepared'),
            ('03_sending', 'Sending'),
            ('04_sent', 'Sent'),
        ],
        string='Status',
        required=True,
        default='01_draft',
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)',
         'The notification set identifier must be unique.'),
    ]

    def _get_access_token(self):
        credentials_data = self.env['ir.values'].sudo().get_default(
            'oma.configuration', 'firebase_credentials')
        decoded_credentials = base64.b64decode(credentials_data)
        credentials_info = json.loads(decoded_credentials)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=[
                'https://www.googleapis.com/auth/firebase.messaging'])
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    def _send_notification(
        self, token, title, subtitle, body, url_img, url_notification,
            notification_id):
        headers = {
            'Authorization': 'Bearer ' + self._get_access_token(),
            'Content-Type': 'application/json; UTF-8',
        }
        project_id = self.env['ir.values'].sudo().get_default(
            'oma.configuration', 'firebase_project_id')
        endpoint = 'https://fcm.googleapis.com/v1/projects/{}/messages:send'.\
            format(project_id)
        data = {
            'message': {
                'notification': {
                    'title': title,
                    'body': subtitle,
                },
                'data': {
                    'url_img': url_img,
                    'url_notification': url_notification,
                    'notification_id': str(notification_id),
                    'html_body': body,
                },
                'token': token,
            }
        }
        resp = requests.post(endpoint, data=json.dumps(data), headers=headers)
        return resp

    @api.multi
    def action_prepare(self):
        for record in self:
            if record.state == '01_draft':
                record.state = '02_prepared'
                notifications = []
                for token in record.token_ids:
                    notification = self.env['oma.notification'].create({
                        'name': record.name + '_' + token.name,
                        'title': record.title,
                        'subtitle': record.subtitle,
                        'url_img': record.url_img,
                        'url_notification': record.url_notification,
                        'notificationset_id': record.id,
                        'send_date': record.send_date,
                        'token_id': token.id,
                        'body': record.body,
                        'state': '02_prepared',
                    })
                    notifications.append(notification)
                record.notification_ids = [
                    (6, 0, [n.id for n in notifications])]

    @api.multi
    def action_return_to_draft(self):
        for record in self:
            if any(notification.state in ['04_sent', '99_error']
                   for notification in record.notification_ids):
                raise UserError(
                    'Cannot return to draft because some notifications are '
                    'already sent or in error state.')
            else:
                record.notification_ids.with_context(
                    from_notification_set=True).unlink()
                record.state = '01_draft'

    @api.multi
    def action_send(self):
        for record in self:
            if record.state == '02_prepared':
                record.state = '03_sending'
                record.notification_ids.action_send()
                record.state = '04_sent'

    @api.multi
    def action_resend(self):
        for record in self:
            if record.state == '04_sent':
                error_notifications = record.notification_ids.filtered(
                    lambda n: n.state == '99_error')
                if error_notifications:
                    record.state = '03_sending'
                    error_notifications.action_send()
                    record.state = '04_sent'

    @api.multi
    def action_get_notifications(self):
        self.ensure_one()
        id_tree_view = self.env.ref(
            'odoo_mobile_app.'
            'oma_notification_tree_view').id
        id_form_view = self.env.ref(
            'odoo_mobile_app.'
            'oma_notification_form_view').id
        search_view = self.env.ref(
            'odoo_mobile_app.'
            'oma_notification_search_view')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Notifications'),
            'res_model': 'oma.notification',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree'), (id_form_view, 'form')],
            'search_view_id': (search_view.id, search_view.name),
            'target': 'current',
            'domain': [('id', 'in', self.notification_ids.ids)],
            'context': {'default_zone_id': self.id}
            }
        return act_window
