# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


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
        size=12,
        help="Limit to 12 characters")

    test_phone_number = fields.Char(
        string="Test phone number",
        size=15,
        help="Used to test configuration.\nOnly Spanish mobile numbers")

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

