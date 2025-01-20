# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http, _
from odoo.http import request


class OmaTokenController(http.Controller):
    @http.route('/api/register_token', type='json',
                auth='public', methods=['POST'], csrf=False)
    def register_token(self, **kwargs):
        token = request.jsonrequest.get('token')
        device_type = request.jsonrequest.get('device_type')
        if device_type not in ['01_android', '02_ios', '99_unknown']:
            return {'status': _('error'),
                    'message':
                    _('Invalid device type. Allowed values are 01_android, '
                      '02_ios or 99_unknown.'
                      )}
        if not token or not device_type:
            return {'status': _('error'),
                    'message':
                    _('Missing parameters: token and device_type are required.'
                      )
                    }

        existing_token = \
            request.env['oma.token'].sudo().search([('name', '=', token)])
        if not existing_token:
            request.env['oma.token'].sudo().create({
                'name': token,
                'device_type': device_type,
            })
            return {'status': _('ok'),
                    'message': _('Token created correctly.')}

        return {'status': _('error'),
                'message': _('Token already exists.')}

    @http.route('/api/register_event', type='json',
                auth='public', methods=['POST'], csrf=False)
    def register_event(self, **kwargs):
        notification_id = request.jsonrequest.get('notification_id')
        event_type = request.jsonrequest.get('event_type')

        if not notification_id or not event_type:
            return {'status': _('error'),
                    'message':
                    _('Missing parameters: notification_id'
                      'and event_type are required.')}
        if event_type not in ['read', 'error', 'received']:
            return {'status': _('error'),
                    'message':
                    _('Invalid event type. Allowed values are read or error.')}
        existing_notification = \
            request.env['oma.notification'].sudo().search(
                [('id', '=', notification_id)])
        if not existing_notification:
            return {'status': _('error'),
                    'message':
                    _('Notification not found. Invalid notification_id.')}
        request.env['oma.notification.event'].sudo().create({
            'notification_id': notification_id,
            'event_type': event_type,
        })
        new_notification_state = False
        if (event_type == 'received'):
            new_notification_state = '05_received'
        elif (event_type == 'read'):
            new_notification_state = '06_read'
        elif (event_type == 'error'):
            new_notification_state = '99_error'
        if new_notification_state:
            existing_notification.write({'state': new_notification_state})
        return {'status': _('ok'),
                'message': _('Event created correctly.')}
