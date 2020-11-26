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
        string="Sender",
        required=True,
        size=15,
        help="The sender that will appear in all messages. Limit to 15 "
             "numbers (only numbers) or 11 alphanumeric characters.")

    test_phone_number = fields.Char(
        string="Test phone number",
        size=15,
        help="Used to test configuration.\nOnly Spanish mobile numbers")

    default_partner_template_id = fields.Many2one(
        comodel_name='wausms.template',
        string='Partner',
        ondelete="set null")

    default_invoice_template_id = fields.Many2one(
        comodel_name='wausms.template',
        string='Invoice',
        ondelete="set null")

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
                           'default_partner_template_id',
                           self.default_partner_template_id.id)
        values.set_default('wau.sms.configuration',
                           'default_invoice_template_id',
                           self.default_invoice_template_id.id)

    @api.constrains('default_sender')
    def _check_default_sender_size(self):
        if not self.default_sender.isdigit() and len(self.default_sender) > 11:
            raise ValidationError(_("Sender size is limited to 15 numbers "
                                    "(ex. 34XXXXXXXXX) or 11 alphanumeric "
                                    "characters (ex. company xxx)"))
