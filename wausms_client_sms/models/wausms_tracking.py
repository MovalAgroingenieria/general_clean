# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class WauSMSTracking(models.Model):
    _name = "wausms.tracking"
    _description = "Tracking of SMS sent"

    name = fields.Char(
        string="SMS id",
        readonly=True,
        help="SMS id assigned by WauSMS service")

    wausms_user = fields.Char(
        string="WauSMS user",
        readonly=True,
        help="The WauSMS user used in credentials")

    wausms_url = fields.Char(
        string="WauSMS URL",
        readonly=True,
        help="The URL used to contect WauSMS service")

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        store=True,
        help="The user who sent the sms")

    sms_time_data = fields.Datetime(
        string="Date",
        readonly=True,
        help="Date on which SMS was sent")

    credentials = fields.Char(
        string="Credentials",
        readonly=True,
        help="Credentials used (b64 encoded)")

    subject = fields.Char(
        string="Subject",
        readonly=True,
        help="Subject used")

    partner_id = fields.Many2one(
        string='Partner',
        store=True,
        index=True,
        comodel_name='res.partner')

    invoice_id = fields.Many2one(
        string='Invoice',
        store=True,
        index=True,
        comodel_name='account.invoice')

    phone_number = fields.Char(
        string="Phone number",
        readonly=True,
        help="Phone number used")

    sender = fields.Char(
        string="From",
        readonly=True,
        help="Sender used")

    sms_message = fields.Text(
        string="Message",
        readonly=True,
        help="Message sent")

    response_code = fields.Text(
        string="Response",
        store=True,
        readonly=True)

    sms_confirmation = fields.Text(
        string="SMS confirmation",
        readonly=True)

    sms_confirmation_info = fields.Text(
        string="SMS confirmation",
        readonly=True)

    response_message = fields.Text(
        string="Response message",
        readonly=True)
