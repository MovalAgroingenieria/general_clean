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
from jinja2 import Template, TemplateError
from lxml import etree


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

    def _get_default_template_id(self):
        context = self._context
        default_template_id = ""
        if context.get("mode") == 'partner':
            default_template_id = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'default_partner_template_id')
        if context.get("mode") == 'invoice':
            default_template_id = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'default_invoice_template_id')
        return default_template_id

    def _default_is_test_wizard(self):
        context = self._context
        is_test_wizard = False
        if context.get("mode") == 'test':
            is_test_wizard = True
        return is_test_wizard

    credentials = fields.Char(
        string="Credentials",
        compute="_compute_credentials")

    subject = fields.Char(
        string="Subject",
        size=100,
        help="Subject description (It is not sent, but it will be searchable "
             "in the tracking system.)")

    phone_number = fields.Char(
        string="Phone number",
        size=15,
        compute="_compute_phone_number",
        help="Only for Spanish mobile numbers")

    sender = fields.Char(
        string="From",
        compute="_compute_sender")

    sms_message = fields.Text(
        string="Message",
        help="The maximum size is 160 characters after resolving variables. "
             "Some special characters will not be displayed.")

    template_id = fields.Many2one(
        comodel_name='wausms.template',
        string='Template',
        default=_get_default_template_id,
        ondelete="set null")

    is_test_wizard = fields.Boolean(
        string="Test wizard",
        default=_default_is_test_wizard)

    @api.onchange('template_id')
    def _compute_template_id_fields(self):
        template = self.env['wausms.template'].browse(self.template_id.id)
        for record in self:
            record.subject = template.subject
            record.sms_message = template.template

    @api.multi
    def _compute_sender(self):
        default_sender = self.env['ir.values'].get_default(
            'wau.sms.configuration', 'default_sender')
        if not default_sender:
            raise ValidationError(_("No sender has been set."))
        for record in self:
            record.sender = default_sender

    @api.multi
    def _compute_credentials(self):
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

    def _compute_sms_template(self, context):
        if context.get("mode") == 'invoice':
            invoice_template = self.env['ir.values'].get_default(
                'wau.sms.configuration', 'default_invoice_template')
            for record in self:
                record.sms_message = invoice_template

    def _escape_json_special_chars(self, string):
        escaped_string = string.replace('\n', '\\n').replace(
            '"', '\\"').replace('\b', '\\b').replace(
            '\t', '\\t').replace('\f', '\\f').replace('\r', '\\r')
        return escaped_string

    def _get_confirmation_messages(self, response_code):
        sms_confirmation = ""
        sms_confirmation_info = ""
        if response_code == 202:
            sms_confirmation = _("Accepted")
            sms_confirmation_info = \
                _("Accepted - The message has been accepted for further "
                  "processing.")
        elif response_code == 207:
            sms_confirmation = _("Multi-status")
            sms_confirmation_info = \
                _("Multi-status - The message has been accepted for further "
                  "processing, but some of the recipients are incorrect.")
        elif response_code == 400:
            sms_confirmation = _("Bad request")
            sms_confirmation_info = \
                _("Bad request - The request contains errors, the message has "
                  "not been accepted.")
        elif response_code == 401:
            sms_confirmation = _("Unauthorized")
            sms_confirmation_info = \
                _("Unauthorized - Client authentication failed.")
        elif response_code == 402:
            sms_confirmation = _("Payment required")
            sms_confirmation_info = \
                _("Payment required - The client does not have sufficient "
                  "balance.")
        elif response_code == 500:
            sms_confirmation = _("Internal server error")
            sms_confirmation_info = \
                _("Internal server error - The server had an internal error.")
        else:
            sms_confirmation = sms_confirmation_info = _("Unknown error")
        return sms_confirmation, sms_confirmation_info

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        context = self._context
        if context.get('mode') == 'partner':
            context_filter = "[('type', '=', 'partner')]"
        elif context.get('mode') == 'invoice':
            context_filter = "[('type', '=', 'invoice')]"
        else:
            context_filter = ""
        res = super(WauSMSWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='template_id']"):
            node.set('domain', context_filter)
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def send_sms_action(self, context):
        service_url = self.env['ir.values'].get_default(
            'wau.sms.configuration', 'service_url')
        wausms_user = self.env['ir.values'].get_default(
            'wau.sms.configuration', 'service_user')
        sender = self.sender
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Basic '+self.credentials, }
        subject = self.subject

        # Reset variables
        active_ids = ""
        raw_sms_message = ""
        sms_confirmations = ""
        response_messages = ""

        # Set active_ids
        if context.get("mode") == 'test':
            active_ids = (0,)
        if context.get("mode") == 'partner':
            invoice_id = False
            active_ids = context.get('active_ids')
        if context.get("mode") == 'invoice':
            partner_active_ids = []
            partner_invoice_list = []
            invoice_ids = context.get('active_ids')
            for invoice_id in invoice_ids:
                invoice = self.env['account.invoice'].browse(invoice_id)
                partner_active_ids.append(invoice.partner_id.id)
                partner_invoice_list.append([invoice.partner_id.id,
                                             invoice_id])
            # Set active_ids as list of list [[partner_id, invoice_id],)
            active_ids = partner_invoice_list
        if not active_ids:
            raise ValidationError(_("There are no items selected."))

        for active_id in active_ids:
            # Set active partner and invoice (x_id is for tracking)
            if context.get("mode") == 'test':
                partner = partner_id = ""
                invoice = invoice_id = ""
            if context.get("mode") == 'partner':
                partner = self.env['res.partner'].browse(active_id)
                partner_id = partner.id
                invoice = invoice_id = ""
            if context.get("mode") == 'invoice':
                partner = self.env['res.partner'].browse(active_id[0])
                partner_id = partner.id
                invoice = self.env['account.invoice'].browse(active_id[1])
                invoice_id = invoice.id
            # Set and check mobile number
            if context.get("mode") == 'test':
                phone_number = self.env['ir.values'].get_default(
                    'wau.sms.configuration', 'test_phone_number')
                if not phone_number:
                    raise ValidationError(
                        _("The phone number for testing has not been set."))
            else:
                if partner.mobile:
                    phone_number = partner.mobile
                else:
                    raise ValidationError(_("Partner %s does not have a "
                                            "mobile number" % partner.name))
            reformated_phone_number = self._check_phone_number(phone_number)

            # Resolve template
            if self.sms_message:
                raw_template = Template(self.sms_message)
                try:
                    raw_sms_message = raw_template.render(
                        partner=partner, invoice=invoice, datetime=datetime)
                except TemplateError as err:
                    raise ValidationError(
                        _("Error resolving template: {}".format(err.message)))
            else:
                sms_message = _('empty message')

            # Eliminate json special characters
            if raw_sms_message:
                sms_message = self._escape_json_special_chars(raw_sms_message)

            # Check size
            if len(sms_message) > 160:
                raise ValidationError(
                    _("Number of characters must not exceed 160"))

            # Encode json
            data_raw = {
                "to": [reformated_phone_number],
                "text": sms_message,
                "from": sender,
                "trsec": "1"}
            data = json.dumps(data_raw)

            # Send and catch response
            response = requests.post(service_url, headers=headers, data=data)

            # Get confirmations messages based in response status code
            sms_confirmation, sms_confirmation_info = \
                self._get_confirmation_messages(response.status_code)

            # Add sms_confirmation message to sms_confirmations
            if context.get("mode") == 'test':
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + "]" + '\n'
            if context.get("mode") == 'partner':
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + " - " + \
                    partner.name + "]" + '\n'
            if context.get("mode") == 'invoice':
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + " - " + \
                    str(invoice.number) + " - " + partner.name + "]" + '\n'

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
            tracking_data = {
                "name": response_message_data["id"],
                "wausms_url": service_url,
                "wausms_user": wausms_user,
                "user_id": self._uid,
                "sms_time_data": datetime.today(),
                "credentials": self.credentials,
                "subject": subject,
                "partner_id": partner_id,
                "invoice_id": invoice_id,
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
