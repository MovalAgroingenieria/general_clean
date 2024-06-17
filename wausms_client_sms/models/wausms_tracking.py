# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from lxml import etree


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
        help="The URL used to connect WauSMS service")

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        store=True,
        help="The user who sent the SMS")

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
        help="The phone number to which the SMS was sent")

    sender = fields.Char(
        string="From",
        readonly=True,
        help="Sender used")

    sms_message = fields.Text(
        string="Message",
        readonly=True,
        help="Text of the SMS sent")

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

    @api.model
    def fields_view_get(self, view_id=None,
                        view_type='form', toolbar=False, submenu=False):
        res = super(
            WauSMSTracking, self).fields_view_get(
                view_id=view_id,
                view_type=view_type,
                toolbar=toolbar,
                submenu=submenu)

        # Check if portal user
        is_portal_user = self.env.user.has_group('base.group_portal')
        if not is_portal_user:
            return res

        if view_type == 'form':
            doc = etree.XML(res['arch'])

            for field in ['wausms_user', 'wausms_url', 'user_id']:
                for node in doc.xpath("//field[@name='%s']" % field):
                    node.getparent().remove(node)
            for page in doc.xpath("//page[@name='response_message_tab']"):
                page.getparent().remove(page)

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res
