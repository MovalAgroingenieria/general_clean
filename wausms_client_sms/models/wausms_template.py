# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from jinja2 import Template, TemplateError
from datetime import datetime
import unicodedata
import random
from odoo import models, fields, api, exceptions, _


class WauSMSTemplate(models.Model):
    _name = 'wausms.template'
    _description = "SMS template"

    name = fields.Char(
        string="Name",
        required=True)

    type = fields.Selection([
        ('partner', 'Partner'),
        ('invoice', 'Invoice')],
        string="Type",
        default="partner",
        required=True,
        help="Type of template")

    subject = fields.Char(
        string="Subject",
        size=100,
        help="Subject of SMS. Limit to 100 characters")

    template = fields.Text(
        string="Template",
        help="Template with jinja2 variables.\nLimit to 160 characters after "
             "resolve variables.")

    template_resolved = fields.Text(
        string="Template resolved",
        readonly=True,
        help="The template after resolve variables using random item.")

    _sql_constraints = [
        ('unique_wausms_template', 'UNIQUE (name, type)', 'Existing template.')
        ]

    def strip_accents(self, string, accents=('COMBINING ACUTE ACCENT',
                                             'COMBINING GRAVE ACCENT')):
        accents = set(map(unicodedata.lookup, accents))
        chars = [c for c in unicodedata.normalize(
            'NFD', string) if c not in accents]
        return unicodedata.normalize('NFC', ''.join(chars))

    def get_random_invoice(self):
        invoice_ids = self.env['account.invoice'].search([], limit=1000).ids
        random_invoice_id = random.choice(invoice_ids)
        invoice = self.env['account.invoice'].browse(random_invoice_id)
        return invoice

    def get_random_partner(self):
        partner_ids = self.env['res.partner'].search([], limit=1000).ids
        random_partner_id = random.choice(partner_ids)
        partner = self.env['res.partner'].browse(random_partner_id)
        return partner

    @api.multi
    def action_resolve_template(self):
        self.ensure_one()
        raw_template = ""
        msg = ""
        raw_sms_message = ""
        sms_message = ""
        if self.template:
            raw_template = Template(self.template)
        if raw_template and self.type == 'partner':
            partner = self.get_random_partner()
            try:
                msg = raw_template.render(
                    partner=partner, datetime=datetime)
            except TemplateError as err:
                raise exceptions.ValidationError(
                    _("Error resolving template: {}".format(err.message)))
            raw_sms_message = msg
        if raw_template and self.type == 'invoice':
            invoice = self.get_random_invoice()
            partner = self.env['res.partner'].browse(invoice.partner_id.id)
            try:
                msg = raw_template.render(
                    partner=partner, invoice=invoice, datetime=datetime)
            except TemplateError as err:
                raise exceptions.ValidationError(
                    _("Error resolving template: {}".format(err.message)))
            raw_sms_message = msg
        # Escape json special chars and accents
        if raw_sms_message:
            sms_message = \
                raw_sms_message.replace('\n', '\\n').replace(
                    '"', '\\"').replace('\b', '\\b').replace(
                    '\t', '\\t').replace('\f', '\\f').replace('\r', '\\r')
            sms_message = self.strip_accents(sms_message)
        # Check size
        if len(sms_message) > 160:
            raise exceptions.ValidationError(
                _('The size of the SMS after solving the variables exceeds '
                  '160 characters. Try setting a fixed length for variables '
                  '{{ object.attribute[:10] }}'))
        if sms_message:
            self.template_resolved = sms_message
