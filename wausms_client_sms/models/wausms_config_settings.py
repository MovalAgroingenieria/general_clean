# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WauSMSConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'wau.sms.configuration'

    service_url = fields.Char(
        string="Service URL",
        required=True)

    service_user = fields.Char(
        string="User",
        required=True)

    service_passwd = fields.Char(
        string="Password",
        required=True)

    default_sender = fields.Char(
        string="Default sender",
        required=True,
        size=15,
        help="Limit to 15 numbers (only numbers) or 11 alphanumeric "
             "characters.")

    default_subject = fields.Char(
        string="Default subject",
        size=100,
        help="Limit to 100 characters")

    test_phone_number = fields.Char(
        string="Test phone number",
        size=15,
        help="Used to test configuration.\nOnly Spanish mobile numbers")

    invoice_subject = fields.Char(
        string="Invoice subject",
        size=100,
        help="Limit to 100 characters")

    invoice_template = fields.Text(
        string="Invoice template",
        help="Template with jinja2 variables for invoice SMS.\nLimit to 160 "
             "characters")

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('wau.sms.configuration',
                           'service_url',
                           self.service_url)
        values.set_default('wau.sms.configuration',
                           'service_user',
                           self.service_user)
        values.set_default('wau.sms.configuration',
                           'service_passwd',
                           self.service_passwd)
        values.set_default('wau.sms.configuration',
                           'default_sender',
                           self.default_sender)
        values.set_default('wau.sms.configuration',
                           'test_phone_number',
                           self.test_phone_number)
        values.set_default('wau.sms.configuration',
                           'default_subject',
                           self.default_subject)
        values.set_default('wau.sms.configuration',
                           'invoice_subject',
                           self.invoice_subject)
        values.set_default('wau.sms.configuration',
                           'invoice_template',
                           self.invoice_template)

    @api.constrains('default_sender')
    def _check_default_sender_size(self):
        if not self.default_sender.isdigit() and len(self.default_sender) > 11:
            raise ValidationError(_("Sender size is limited to 15 numbers "
                                    "(ex. 34XXXXXXXXX) or 11 alphanumeric "
                                    "characters (ex. company xxx)"))

    @api.constrains('default_subject')
    def _check_default_subject_size(self):
        if self.default_subject and len(self.default_subject) > 99:
            raise ValidationError(_("Default subject is limited to 100 "
                                    "characters"))

    @api.constrains('invoice_subject')
    def _check_invoice_subject_size(self):
        if self.invoice_subject and len(self.invoice_subject) > 99:
            raise ValidationError(_("Invoice subject is limited to 100 "
                                    "characters"))
