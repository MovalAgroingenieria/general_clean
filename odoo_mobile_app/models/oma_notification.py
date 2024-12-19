# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import UserError


class OmaNotification(models.Model):
    _name = 'oma.notification'
    _description = 'Individual Notification'

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
    token_id = fields.Many2one(
        comodel_name='oma.token',
        string='Device Token',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('01_draft', 'Draft'),
            ('02_prepared', 'Prepared'),
            ('03_sending', 'Sending'),
            ('04_sent', 'Sent'),
            ('05_received', 'Received'),
            ('06_read', 'Read'),
            ('99_error', 'Error'),
        ],
        string='Status',
        required=True,
        default='01_draft',
    )

    notificationset_id = fields.Many2one(
        string='Notification Set',
        comodel_name='oma.notification.set',
        ondelete='restrict',
    )

    notificationevent_ids = fields.One2many(
        string='Events',
        comodel_name='oma.notification.event',
        inverse_name='notification_id',
    )

    _sql_constraints = [
        ('unique_name', 'unique(name)',
         'The notification identifier must be unique.'),
    ]

    @api.multi
    def action_prepare(self):
        self.write({'state': '02_prepared'})

    @api.multi
    def action_return_to_draft(self):
        if self.notificationset_id:
            raise UserError(
                'Cannot return to draft because the notification'
                ' is assigned to a notification set.')
        self.write({'state': '01_draft'})

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
            try:
                resp = self.env['oma.notification.set']._send_notification(
                    token, title, subtitle, body, url_img, url_notification,
                    notification_id)
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

    @api.multi
    def action_resend(self):
        for record in self:
            if record.state == '99_error':
                self.action_send()
            else:
                raise UserError(
                    'Cannot resend a notification that is not in error state.')

    @api.multi
    def unlink(self):
        for record in self:
            if record.notificationset_id:
                if not self.env.context.get('from_notification_set'):
                    raise UserError(
                        'Cannot delete a notification that'
                        ' is assigned to a notification set.')
        return super(OmaNotification, self).unlink()
