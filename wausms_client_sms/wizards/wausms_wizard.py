# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import requests
import json
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type


class WauSMSConfirmation(models.Model):
    _name = "wausms.confirmation"
    _description = "Response to SMS sent"

    response_code = fields.Text(
        string="Response",
        readonly=True)

    response_message = fields.Text(
        string="Response message",
        readonly=True)


class WauSMSWizard(models.Model):
    _name = "wausms.wizard"
    _description = "Wizard to send SMS through WauSMS service"

    def _get_default_sender(self):
        default_sender = self.env['ir.values'].get_default(
            'wau.sms.configuration', 'default_sender')
        if not default_sender:
            default_sender = "Unconfigured"
        return default_sender

    credentials = fields.Char(
        string="Credentials",
        compute="_compute_credentials")

    phone_number = fields.Char(
        string="Phone number",
        size=15,
        compute="_compute_phone_number",
        help="Only for Spanish mobile numbers")

    sender = fields.Char(
        string="From",
        size=15,
        required=True,
        default=_get_default_sender)

    sms_message = fields.Text(
        string="Message",
        size=160)

    def _compute_credentials(self):
        # Get config params
        service_user = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'service_user')
        service_passwd = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'service_passwd')

        if not service_user or not service_passwd:
            raise ValidationError(_("User or password not set."))
        else:
            self.credentials = \
                base64.b64encode(service_user + ':' + service_passwd)

    def _check_phone_number(self, phone_number):
        # Check if only digits
        if phone_number.startswith('+'):
            phone_number = phone_number.strip('+')
        if not phone_number.isdigit():
            raise ValidationError(_("Error in phone number, there are "
                                    "characters that are not digits."))

        # Reformat phone number to E.164
        reformated_phone_number = phonenumbers.format_number(
                phonenumbers.parse(phone_number, "ES"),
                phonenumbers.PhoneNumberFormat.E164)
        if not carrier._is_mobile(number_type(
               phonenumbers.parse(reformated_phone_number, "ES"))):
            raise ValidationError(_("Error in phone number, or is not a "
                                    "mobile, or is not Spanish or does not "
                                    "have the correct format."))
        if reformated_phone_number.startswith('+'):
            reformated_phone_number = reformated_phone_number.strip('+')
        return reformated_phone_number

    @api.multi
    def send_sms_action(self, context):
        if context.get("mode") == 'test':
            # Get test phone number
            test_phone_number = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'test_phone_number')
            if not test_phone_number:
                raise ValidationError(_("No test phone number has been set."))
            active_ids = (0,)
        else:
            active_ids = context.get('active_ids')

        if not active_ids:
            raise ValidationError(_("There are no parters selected."))

        # Reset variables
        sms_confirmations = ""
        response_messages = ""

        for id in active_ids:
            if id == 0:
                phone_number = test_phone_number
            else:
                # Get partner data
                partner = self.env['res.partner'].browse(id)

                # Get mobile number
                if partner.mobile:
                    phone_number = partner.mobile
                else:
                    raise ValidationError(_("Partner %s does not have a "
                                            "mobile number" % partner.name))

            # Check phone number
            reformated_phone_number = \
                self._check_phone_number(phone_number)

            # Check sender
            if not self.sender:
                sender = self._get_default_sender()
                if not sender:
                    raise ValidationError(_("No sender has been set."))
            else:
                sender = self.sender

            # Change sms message encoding
            if self.sms_message:
                sms_message = self.sms_message.encode('ascii', 'replace')
            else:
                sms_message = "empty message".encode('ascii', 'replace')

            # Get URL from cofig parm
            service_url = self.env['ir.values'].get_default(
                    'wau.sms.configuration', 'service_url')

            # Header
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Basic '+self.credentials,
            }

            # Data
            data = \
                '{"to":[ "%s" ], "text": "%s", "from": "%s", "trsec": "1"}' % \
                (reformated_phone_number, sms_message, sender)

            # Send and catch response
            response = requests.post(service_url, headers=headers, data=data)

            # Response codes
            if response.status_code == 202:
                sms_confirmation = _("Accepted - The message has been "
                                     "accepted for further processing.")
            elif response.status_code == 207:
                sms_confirmation = _("Multi-status - The message has been "
                                     "accepted for further processing, but "
                                     "some of the recipients are incorrect.")
            elif response.status_code == 400:
                sms_confirmation = _("Bad request - The request contains "
                                     "errors, the message has not been "
                                     "accepted.")
            elif response.status_code == 401:
                sms_confirmation = _("Unauthorized - Client authentication "
                                     "failed.\n")
            elif response.status_code == 402:
                sms_confirmation = _("Payment required - The client does not "
                                     "have sufficient balance.")
            elif response.status_code == 500:
                sms_confirmation = _("Internal server error - The server had "
                                     "an internal error.")
            else:
                sms_confirmation = _("Unknown error")

            # Add sms_confirmation message to sms_confirmations
            if id == 0:
                sms_confirmations += sms_confirmation + '\n'
            else:
                sms_confirmations += \
                    sms_confirmation + " [" + partner.name + "]" + '\n'

            # Response message (only shown in debug mode)
            response_message = json.dumps(response.json(), indent=4)

            # Add sms_confirmation message to sms_confirmations
            if id == 0:
                response_messages += response_message + "\n"
            else:
                response_messages += \
                    partner.name + '\n' + response_message + "\n"

        return {
              'name': _("SMS confirmation"),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'wausms.confirmation',
              'type': 'ir.actions.act_window',
              'context': {'default_response_code': '%s' % sms_confirmations,
                          'default_response_message': '%s' % response_messages
                          },
              'target': 'new',
              }

    @api.constrains('sms_message')
    def _check_sms_message_size(self):
        if len(self.sms_message) > 160:
            raise ValidationError(_("Number of characters must not exceed "
                                    "160"))

