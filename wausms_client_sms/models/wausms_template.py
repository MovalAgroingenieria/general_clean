# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from jinja2 import Template, TemplateError
from datetime import datetime
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

    def _escape_json_special_chars(self, string):
        escaped_string = string.replace('\n', '\\n').replace(
            '"', '\\"').replace('\b', '\\b').replace(
            '\t', '\\t').replace('\f', '\\f').replace('\r', '\\r')
        return escaped_string

    def _get_random_invoice(self):
        invoice = ""
        invoice_ids = self.env['account.invoice'].search([], limit=1000).ids
        if len(invoice_ids) > 0:
            random_invoice_id = random.choice(invoice_ids)
            invoice = self.env['account.invoice'].browse(random_invoice_id)
        else:
            raise exceptions.ValidationError(_("No invoice found"))
        return invoice

    def _get_random_partner(self):
        partner = ""
        partner_ids = self.env['res.partner'].search([], limit=1000).ids
        if len(partner_ids) > 0:
            random_partner_id = random.choice(partner_ids)
            partner = self.env['res.partner'].browse(random_partner_id)
        else:
            raise exceptions.ValidationError(_("No partner found"))
        return partner

    @api.multi
    def action_resolve_template(self):
        self.ensure_one()
        partner = invoice = raw_message = message = ""
        if self.template:
            template = Template(self.template)
        if self.type == 'partner':
            partner = self._get_random_partner()
            try:
                raw_message = template.render(
                    partner=partner, datetime=datetime)
            except TemplateError as err:
                raise exceptions.ValidationError(
                    _("Error resolving template: {}".format(err.message)))
        if self.type == 'invoice':
            invoice = self._get_random_invoice()
            partner = self.env['res.partner'].browse(invoice.partner_id.id)
            try:
                raw_message = template.render(
                    partner=partner, invoice=invoice, datetime=datetime)
            except TemplateError as err:
                raise exceptions.ValidationError(
                    _("Error resolving template: {}".format(err.message)))
        if raw_message:
            message = self._escape_json_special_chars(raw_message)
        if len(message) > 160:
            raise exceptions.ValidationError(
                _('The size of the SMS after solving the variables exceeds '
                  '160 characters. Try setting a fixed length for variables '
                  '{{ object.attribute[:10] }}'))
        if message:
            self.template_resolved = message
