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
from datetime import datetime


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

    def _get_default_subject(self):
        default_subject = self.env['ir.values'].get_default(
            'wau.sms.configuration', 'default_subject')
        return default_subject

    def _get_default_sender(self):
        default_sender = self.env['ir.values'].get_default(
            'wau.sms.configuration', 'default_sender')
        if not default_sender:
            default_sender = "Unconfigured"
        return default_sender

    credentials = fields.Char(
        string="Credentials",
        compute="_compute_credentials")

    subject = fields.Char(
        string="Subject",
        size=100,
        default=_get_default_subject,
        help="Subject description (will be searchable in tracking system)")

    phone_number = fields.Char(
        string="Phone number",
        size=15,
        compute="_compute_phone_number",
        help="Only for Spanish mobile numbers")

    sender = fields.Char(
        string="From",
        size=15,
        required=True,
        readonly=True,
        default=_get_default_sender,
        help="The sender that will appear in the message.")

    sms_message = fields.Text(
        string="Message",
        size=160,
        help="The maximum size is 160 characters. The message will be sent in "
             "ASCII, so the special characters will not be displayed.")

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
        # Checks
        phone_number = phone_number.replace(" ", "").strip()
        if phone_number.startswith('+'):
            phone_number = phone_number.strip('+')
        if not phone_number.isdigit():
            raise ValidationError(_("Error in phone number, there are "
                                    "characters that are not digits."))

        # Reformat phone number to E.164
        reformated_phone_number = phonenumbers.format_number(
            phonenumbers.parse(phone_number, "ES"),
            phonenumbers.PhoneNumberFormat.E164)
        if (not carrier._is_mobile(
           number_type(phonenumbers.parse(reformated_phone_number, "ES")))):
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
            # Get default subject
            default_subject = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'default_subject')
            # Set active_ids to 0
            active_ids = (0,)
        else:
            # Get active_ids
            active_ids = context.get('active_ids')

        if not active_ids:
            raise ValidationError(_("There are no partners selected."))

        # Reset variables
        sms_confirmations = ""
        response_messages = ""

        for active_id in active_ids:
            if active_id == 0:
                phone_number = test_phone_number
                subject = default_subject
                if not subject:
                    subject = ""
            else:
                # Get subject
                if self.subject:
                    subject = self.subject
                else:
                    subject = ""

                # Get partner data
                partner = self.env['res.partner'].browse(active_id)

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

            # Change sms message encoding and escape json special chars
            if self.sms_message:
                sms_message = \
                    self.sms_message.replace('\n', '\\n').replace(
                        '"', '\\"').replace('\b', '\\b').replace(
                        '\t', '\\t').replace('\f', '\\f').replace('\r', '\\r')
                sms_message = sms_message.encode('ascii', 'replace')
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
                sms_confirmation_info = _("Accepted - The message has been "
                                          "accepted for further processing.")
                sms_confirmation = _("Accepted")
            elif response.status_code == 207:
                sms_confirmation_info = _("Multi-status - The message has "
                                          "been accepted for further "
                                          "processing, but some of the "
                                          "recipients are incorrect.")
                sms_confirmation = _("Multi-status")
            elif response.status_code == 400:
                sms_confirmation_info = _("Bad request - The request contains "
                                          "errors, the message has not been "
                                          "accepted.")
                sms_confirmation = _("Bad request")
            elif response.status_code == 401:
                sms_confirmation_info = _("Unauthorized - Client "
                                          "authentication failed.")
                sms_confirmation = _("Unauthorized")
            elif response.status_code == 402:
                sms_confirmation_info = _("Payment required - The client does "
                                          "not have sufficient balance.")
                sms_confirmation = _("Payment required")
            elif response.status_code == 500:
                sms_confirmation_info = _("Internal server error - The server "
                                          "had an internal error.")
                sms_confirmation = _("Internal server error")
            else:
                sms_confirmation_info = sms_confirmation = _("Unknown error")

            # Add sms_confirmation message to sms_confirmations
            if active_id == 0:
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + "]" + '\n'
            else:
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + " - " + \
                    partner.name + "]" + '\n'

            # Response message (only shown in debug mode)
            response_message = json.dumps(response.json(), indent=4)
            if 'error' in response.text:
                response_message_data = json.loads(response.text)
                response_message_data['id'] = "no-id"
            else:
                response_message_data = json.loads(response.text)[0]

            # Add sms_confirmation message to sms_confirmations
            if active_id == 0:
                response_messages += "Subject: " + subject + '\n' \
                                     "Sender: " + sender + '\n' \
                                     "To: " + reformated_phone_number + '\n' \
                                     "Response: " + response_message + '\n'
            else:
                response_messages += "Subject: " + subject + '\n' \
                                     "Sender: " + sender + '\n' \
                                     "To: " + reformated_phone_number + '\n' \
                                     "Partner: " + partner.name + '\n' \
                                     "Confirmation: " + sms_confirmation_info \
                                     + '\n' \
                                     "Response: " + '\n' + response_message \
                                     + '\n'

            # Insert tracking data
            if active_id == 0:
                partner_id = ""
            else:
                partner_id = partner.id

            wausms_user = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'service_user')

            tracking_data = {
                "wausms_sms_id": response_message_data["id"],
                "wausms_url": service_url,
                "wausms_user": wausms_user,
                "user_id": self._uid,
                "sms_time_data": datetime.today(),
                "credentials": self.credentials,
                "subject": subject,
                "partner_id": partner_id,
                "phone_number": reformated_phone_number,
                "sender": sender,
                "sms_message": sms_message,
                "response_code": response.status_code,
                "sms_confirmation": sms_confirmation,
                "sms_confirmation_info": sms_confirmation_info,
                "response_message": response_message, }
            self.env['wausms.tracking'].create(tracking_data)

        return {
            'name': _("SMS confirmation"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wausms.confirmation',
            'type': 'ir.actions.act_window',
            'context': {
                'default_response_code': '%s' % sms_confirmations,
                'default_response_message': '%s' % response_messages
                },
            'target': 'new',
            }

    @api.constrains('sender')
    def _check_default_sender_size(self):
        if not self.sender.isdigit() and len(self.sender) > 11:
            raise ValidationError(_("Sender size is limited to 15 numbers or "
                                    "11 alphanumeric characters"))

    @api.constrains('sms_message')
    def _check_sms_message_size(self):
        if len(self.sms_message) > 160:
            raise ValidationError(_("Number of characters must not exceed "
                                    "160"))
