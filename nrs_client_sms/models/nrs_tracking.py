# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api , _
from odoo.exceptions import ValidationError
import base64
import requests


class NRSTracking(models.Model):
    _name = "nrs.tracking"
    _description = "Tracking of SMS sent"

    name = fields.Char(
        string="SMS id",
        readonly=True,
        help="SMS id assigned by NRS service")

    nrs_user = fields.Char(
        string="NRS user",
        readonly=True,
        help="The NRS user used in credentials")

    nrs_url = fields.Char(
        string="NRS URL",
        readonly=True,
        help="The URL used to connect NRS service")

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        store=True,
        readonly=True,
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
        readonly=True,
        comodel_name='res.partner')

    invoice_id = fields.Many2one(
        string='Invoice',
        store=True,
        index=True,
        readonly=True,
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

    certified = fields.Boolean(
        string="Certified",
        readonly=True,
        help="It shows if the SMS was certified or not.")

    pdf_certificate = fields.Binary(
        string="PDF certificate",
        attachment=True,
        readonly=True)

    pdf_certificate_name = fields.Char(
        string='PDF certificate name')

    @api.multi
    def get_pdf_certificate(self):
        self.ensure_one()
        headers = {
            'Content-Type': 'application/pdf',
            'Authorization': 'Basic '+self.credentials, }
        cert_url = "https://dashboard.360nrs.com/api/rest/sms/certificates/"
        sms_id = self.name
        if sms_id != "no-id" and self.certified:
            cert_url += sms_id
            pdf = pdf_name = pdf_ready = False
            attempts = 0
            while pdf_ready == False and attempts < 4:
                try:
                    response = requests.get(cert_url, headers=headers)
                    pdf_ready = response.ok
                    attempts += 1
                except requests.exceptions.RequestException as err:
                    raise ValidationError(
                        _("Error getting certificate: "
                          "{}".format(err.message)))
            if pdf_ready:
                pdf = base64.b64encode(response.content)
                pdf_name = sms_id + '.pdf'
                self.pdf_certificate = pdf
                self.pdf_certificate_name = pdf_name
            else:
                raise ValidationError(
                        _("The certificate is not ready yet."))

    def get_pdf_certificates(self, active_ids):
        sms_ids = self.env['nrs.tracking'].browse(active_ids)
        for sms in sms_ids:
            sms.get_pdf_certificate()
