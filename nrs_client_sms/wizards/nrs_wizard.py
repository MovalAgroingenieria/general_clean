# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import requests
import json
import phonenumbers
import re
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
from datetime import datetime
from jinja2 import Template, TemplateError
from lxml import etree


class NRSConfirmation(models.Model):
    _name = "nrs.confirmation"
    _description = "Response to SMS sent"

    response_code = fields.Text(
        string="Response",
        readonly=True)

    response_message = fields.Text(
        string="Response message",
        readonly=True)


class NRSWizard(models.Model):
    _name = "nrs.wizard"
    _description = "Wizard to send SMS through NRS service"

    def _get_default_template_id(self):
        context = self._context
        default_template_id = ""
        if context.get("mode") == 'partner':
            default_template_id = self.env['ir.values'].get_default(
                'nrs.configuration', 'default_partner_template_id')
        if context.get("mode") == 'invoice':
            default_template_id = self.env['ir.values'].get_default(
                'nrs.configuration', 'default_invoice_template_id')
        return default_template_id

    def _default_is_test_wizard(self):
        context = self._context
        is_test_wizard = False
        if context.get("mode") == 'test':
            is_test_wizard = True
        return is_test_wizard

    def _get_default_sender(self):
        default_sender = self.env['ir.values'].get_default(
            'nrs.configuration', 'default_sender')
        return default_sender

    def _default_allow_certify_sms(self):
        allow_certify_sms = self.env['ir.values'].get_default(
            'nrs.configuration', 'allow_certify_sms')
        return allow_certify_sms

    def _default_allow_flash_sms(self):
        allow_flash_sms = self.env['ir.values'].get_default(
            'nrs.configuration', 'allow_flash_sms')
        return allow_flash_sms

    def _default_wizard_mode(self):
        context = self._context
        mode = context.get("mode")
        return mode

    credentials = fields.Char(
        string="Credentials",
        compute="_compute_credentials")

    subject = fields.Char(
        string="Subject",
        size=100,
        help="Subject description (It is not sent, but it will be searchable "
             "in the tracking system.)")

    sender = fields.Char(
        string="From",
        default=_get_default_sender,
        compute="_compute_sender")

    sms_message = fields.Text(
        string="Message",
        help="The maximum size is 160 characters after resolving variables. "
             "Some special characters will not be displayed.")

    template_id = fields.Many2one(
        comodel_name='nrs.template',
        string='Template',
        default=_get_default_template_id,
        ondelete="set null")

    is_test_wizard = fields.Boolean(
        string="Test wizard",
        default=_default_is_test_wizard)

    certify = fields.Boolean(
        string="Certify",
        help="Certify the SMS. It will apply to all selected items. "
             "It has an additional cost.")

    sms_flash = fields.Boolean(
        string="Flash",
        help="The SMS appears directly on the device screen but it is not "
             "saved.")

    allow_certify_sms = fields.Boolean(
        default=_default_allow_certify_sms)

    allow_flash_sms = fields.Boolean(
        default=_default_allow_flash_sms)

    send_invoice_link = fields.Boolean(
        string="Send invoice link",
        help="It will generate a pdf and a link for each invoice. It slows "
             "down the process.")

    wizard_mode = fields.Char(
        default=_default_wizard_mode)

    @api.onchange('template_id')
    def _compute_template_id_fields(self):
        template = self.env['nrs.template'].browse(self.template_id.id)
        for record in self:
            record.subject = template.subject
            record.sms_message = template.template

    @api.onchange('send_invoice_link')
    def _compute_link_tracker_module(self):
        if not self.env.registry.get('link.tracker'):
            raise ValidationError(_("Link tracker is not installed."))

    @api.multi
    def _compute_sender(self):
        default_sender = self._get_default_sender()
        if not default_sender:
            raise ValidationError(_("No sender has been set."))
        for record in self:
            record.sender = default_sender

    @api.multi
    def _compute_credentials(self):
        service_user = self.env['ir.values'].get_default(
            'nrs.configuration', 'service_user')
        service_passwd = self.env['ir.values'].get_default(
            'nrs.configuration', 'service_passwd')

        if not service_user or not service_passwd:
            raise ValidationError(_("User or password not set."))
        else:
            self.credentials = \
                base64.b64encode(service_user + ':' + service_passwd)

    @api.multi
    def _compute_wizard_mode(self):
        context = self._context
        if context.get("mode") == 'test':
            mode = 'test'
        if context.get("mode") == 'partner':
            mode = 'partner'
        if context.get("mode") == 'invoice':
            mode = 'invoice'
        for record in self:
            record.wizard_mode = mode

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

    def _generate_invoice_link(self, invoice_id):
        data = {'res_model': 'account.invoice', 'res_id': invoice_id,
                'mimetype': 'application/pdf', 'public': True}
        self.env['report'].get_pdf([invoice_id], 'account.report_invoice',
                                   data=data)
        attachment = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.invoice'),
             ('res_id', '=', invoice_id)], order='write_date desc', limit=1)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url_raw = base_url + '/web/login?redirect='
        url_download = \
            '/web/binary/download_sms_attachment/' + str(attachment.id)
        link_raw = self.env['link.tracker'].sudo().create(
            {"url": base_url + url_download})
        url_redirect_pdf = url_raw + '/r/' + link_raw.code
        url = (self.env['link.tracker'].sudo().create(
            {"url": url_redirect_pdf}).short_url)
        return url

    def _escape_json_special_chars(self, string):
        escaped_string = string.replace('\n', '\\n').replace(
            '"', '\\"').replace('\b', '\\b').replace(
            '\t', '\\t').replace('\f', '\\f').replace('\r', '\\r')
        return escaped_string

    def _get_confirmation_messages(self, response):
        response_code = response.status_code
        sms_confirmation_info = ""

        if response_code == 202:
            sms_confirmation = _("Accepted")
            sms_confirmation_info = \
                _("Accepted - The message has been accepted for further "
                  "processing.")
        elif response_code == 400:
            sms_confirmation = _("Bad request")
            response_data = json.loads(response.text)
            error_data = json.loads(json.dumps(response_data['error']))
            error_code = error_data['code']
            if error_code == 102:
                sms_confirmation_info = _("Bad request - No valid recipients.")
            elif error_code == 104:
                sms_confirmation_info = \
                    _("Bad request - Text message missing.")
            elif error_code == 105:
                sms_confirmation_info = \
                    _("Bad request - Text message too long.")
            elif error_code == 106:
                sms_confirmation_info = _("Bad request - Sender missing.")
            elif error_code == 107:
                sms_confirmation_info = _("Bad request - Sender too long.")
            elif error_code == 108:
                sms_confirmation_info = \
                    _("Bad request - No valid Datetime for send.")
            elif error_code == 109:
                sms_confirmation_info = \
                    _("Bad request - Notification URL incorrect.")
            elif error_code == 110:
                sms_confirmation_info = \
                    _("Bad request - Exceeded maximum parts allowed or "
                      "incorrect number of parts.")
            elif error_code == 113:
                sms_confirmation_info = _("Bad request - Invalid coding.")
            elif error_code == 120:
                sms_confirmation_info = _("Bad request - Invalid GUID.")
            elif error_code == 121:
                sms_confirmation_info = \
                    _("Bad request - Invalid scheduled date.")
            else:
                sms_confirmation_info = \
                    _("Bad request - Unknown error code.")
        elif response_code == 401:
            sms_confirmation = _("Unauthorized")
            response_data = json.loads(response.text)
            error_data = json.loads(json.dumps(response_data['error']))
            error_code = error_data['code']
            if error_code == 103:
                sms_confirmation_info = \
                    _("Unauthorized - Username or password unknown.")
            elif error_code == 111:
                sms_confirmation_info = \
                    _("Unauthorized - Not enough credits.")
            else:
                sms_confirmation_info = \
                    _("Unauthorized - Unknown error code.")
        elif response_code == 402:
            sms_confirmation = _("Payment required")
            response_data = json.loads(response.text)
            error_data = json.loads(json.dumps(response_data['error']))
            error_code = error_data['code']
            if error_code == 111:
                sms_confirmation_info = \
                    _("Payment required - Not enough credits.")
            else:
                sms_confirmation_info = \
                    _("Payment required - Unknown error code.")
        elif response_code == 500:
            sms_confirmation = _("Internal server error")
            response_data = json.loads(response.text)
            error_data = json.loads(json.dumps(response_data['error']))
            error_code = error_data['code']
            if error_code == 122:
                sms_confirmation_info = \
                    _("Internal server error - Update error.")
            if error_code == 123:
                sms_confirmation_info = \
                    _("Internal server error - Delete error.")
            else:
                sms_confirmation_info = \
                    _("Internal server error - Unknown error code.")
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
        res = super(NRSWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='template_id']"):
            node.set('domain', context_filter)
        res['arch'] = etree.tostring(doc)
        return res

    def _calculate_number_of_sms(self, num_char, encoding):
        if num_char == 0:
            return 0
        if encoding == 'utf-16':
            if num_char <= 70:
                return 1
            return -(-num_char // 67)
        if num_char <= 160:
            return 1
        return -(-num_char // 153)

    def _extract_encoding(self, content):
        if not isinstance(content, unicode):
            content = content.decode('utf-8')

        encoding = 'utf-16'
        gsm7_pattern = re.compile(
            ur"^[@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ "
            ur"!\"#¤%&'()*+,-./0123456789:;<=>?¡"
            ur"ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿"
            ur"abcdefghijklmnopqrstuvwxyzäöñüà]*$")

        if gsm7_pattern.match(content):
            encoding = 'gsm'
        return encoding

    @api.multi
    def send_sms_action(self, context):
        service_url = self.env['ir.values'].get_default(
            'nrs.configuration', 'service_url')
        nrs_user = self.env['ir.values'].get_default(
            'nrs.configuration', 'service_user')
        sender = self.sender
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Basic '+self.credentials, }
        subject = self.subject
        certify = self.certify
        sms_flash = self.sms_flash

        # Reset variables
        active_ids = ""
        raw_sms_message = ""
        sms_confirmations = ""
        response_messages = ""
        num_of_sms = 0

        # Set active_ids
        if self.wizard_mode == 'test':
            active_ids = (0,)
        if self.wizard_mode == 'partner':
            invoice_id = False
            active_ids = context.get('active_ids')
        if self.wizard_mode == 'invoice':
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
            if self.wizard_mode == 'test':
                partner = partner_id = ""
                invoice = invoice_id = ""
            if self.wizard_mode == 'partner':
                partner = self.env['res.partner'].browse(active_id)
                partner_id = partner.id
                invoice = invoice_id = ""
            if self.wizard_mode == 'invoice':
                partner = self.env['res.partner'].browse(active_id[0])
                partner_id = partner.id
                invoice = self.env['account.invoice'].browse(active_id[1])
                invoice_id = invoice.id
                invoice_link = ""
                if self.send_invoice_link:
                    invoice_link = self._generate_invoice_link(invoice_id)

            # Set and check mobile number
            if self.wizard_mode == 'test':
                phone_number = self.env['ir.values'].get_default(
                    'nrs.configuration', 'test_phone_number')
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

            # Add invoice link
            if self.wizard_mode == 'invoice' and invoice_link:
                raw_sms_message += ' ' + invoice_link

            # Eliminate json special characters
            if raw_sms_message:
                sms_message = self._escape_json_special_chars(raw_sms_message)

            # Number of sms
            encoding = self._extract_encoding(sms_message)
            num_char = len(sms_message)
            number_of_sms = self._calculate_number_of_sms(num_char, encoding)

            # Check size
            if len(sms_message) > 1530:
                raise ValidationError(
                    _("Number of characters must not exceed 1530"))

            # Encode json
            data_raw = {
                "to": [reformated_phone_number],
                "from": sender,
                "message": sms_message,
                "certified": certify,
                "encoding": encoding,
                "flash": sms_flash,
                "parts": number_of_sms, }
            data = json.dumps(data_raw)

            # Send and catch response
            response = ""
            connection_error = ""
            connection_ok = False
            try:
                response = requests.post(service_url, headers=headers,
                                         data=data)
                connection_ok = True
            except requests.exceptions.RequestException as requests_error:
                connection_error = requests_error.message.message + '\n'

            # Increase counter
            num_of_sms += 1

            # Get confirmations messages based in response status code
            if connection_ok:
                sms_confirmation, sms_confirmation_info = \
                    self._get_confirmation_messages(response)
                status_code = response.status_code
            else:
                sms_confirmation, sms_confirmation_info = \
                    _('ERROR: no response'), _('ERROR: no response')
                status_code = "error"

            # Add sms_confirmation message to sms_confirmations
            if not subject:
                subject = _('No subject')
            if context.get("mode") == 'test':
                sms_confirmations += str(num_of_sms).zfill(4) + ' -- ' + \
                    sms_confirmation + " -- [" + subject + "]"
            if context.get("mode") == 'partner':
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + " - " + \
                    "Num. " + str(number_of_sms) + " - " + \
                    partner.name + "]" + '\n'
            if context.get("mode") == 'invoice':
                sms_confirmations += \
                    sms_confirmation + " -- [" + subject + " - " + \
                    "Num " + str(number_of_sms) + " - " + \
                    str(invoice.number) + " - " + partner.name + "]" + '\n'

            # Response message (only shown in debug mode)
            if connection_ok:
                response_message = json.dumps(response.json(), indent=4)
                if 'error' in response.text:
                    response_message_data = json.loads(response.text)
                    response_message_data = \
                        json.loads(json.dumps(response_message_data['error']))
                    name_id = "no-id"
                    certify = False
                else:
                    response_message_data = json.loads(response.text)
                    response_message_data = \
                        json.loads(json.dumps(response_message_data['result']))
                    name_id = response_message_data[0]["id"]
            else:
                response_message = _('ERROR: no response')
                certify = False
                if connection_error:
                    response_message += '\n' + connection_error
                name_id = "no-id"

            # Show if it has been certified
            is_certifed = _("No")
            if certify:
                sms_confirmations += _(" [Certified] ") + '\n'
                is_certifed = _("Yes")
            else:
                sms_confirmations += '\n'

            # Add sms_confirmation message to sms_confirmations
            if active_id == 0:
                response_messages += \
                    str(num_of_sms).zfill(4) + \
                    ' --------------------------------' + '\n' + \
                    _("Subject: ") + subject + '\n' + \
                    _("Sender: ") + sender + '\n' + \
                    _("To: ") + reformated_phone_number + '\n' + \
                    _("Certified: ") + is_certifed + '\n' + \
                    _("Number of SMS: ") + str(number_of_sms) + '\n' + \
                    _("Response: ") + response_message + '\n' + '\n'
            else:
                response_messages += \
                    str(num_of_sms).zfill(4) + \
                    ' --------------------------------' + '\n' + \
                    _("Subject: ") + subject + '\n' + \
                    _("Sender: ") + sender + '\n' + \
                    _("To: ") + reformated_phone_number + '\n' + \
                    _("Partner: ") + partner.name + '\n' + \
                    _("Confirmation: ") + sms_confirmation_info + '\n' + \
                    _("Certified: ") + is_certifed + '\n' + \
                    _("Number of SMS: ") + str(number_of_sms) + '\n' + \
                    _("Response: ") + '\n' + response_message + '\n' + '\n'

            # Insert tracking data
            tracking_data = {
                "name": name_id,
                "nrs_url": service_url,
                "nrs_user": nrs_user,
                "user_id": self._uid,
                "sms_time_data": datetime.today(),
                "credentials": self.credentials,
                "subject": subject,
                "certified": certify,
                "partner_id": partner_id,
                "invoice_id": invoice_id,
                "phone_number": reformated_phone_number,
                "sender": sender,
                "sms_message": sms_message,
                "response_code": status_code,
                "sms_confirmation": sms_confirmation,
                "sms_confirmation_info": sms_confirmation_info,
                "response_message": response_message,
                "number_of_sms": number_of_sms, }
            self.env['nrs.tracking'].create(tracking_data)

        return {
            'name': _("SMS confirmation"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nrs.confirmation',
            'type': 'ir.actions.act_window',
            'context': {
                'default_response_code': '%s' % sms_confirmations,
                'default_response_message': '%s' % response_messages
                },
            'target': 'new',
            }
