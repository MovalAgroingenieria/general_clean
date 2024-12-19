# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class OmaNotificationEvent(models.Model):
    _name = 'oma.notification.event'
    _description = 'Notification Event'
    _order = 'event_time asc'

    notification_id = fields.Many2one(
        comodel_name='oma.notification',
        string='Notification',
        required=True,
        ondelete='cascade',
    )

    # Should this be a selection?
    # types: send, error, received, read
    event_type = fields.Char(
        string='Event Type',
        required=True,
    )

    event_message = fields.Char(
        string='Event Message',
    )

    event_time = fields.Datetime(
        string='Event Time',
        required=True,
        default=fields.Datetime.now,
    )
