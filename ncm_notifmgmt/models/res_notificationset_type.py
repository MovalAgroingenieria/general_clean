# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
from time import time
from jinja2 import Template, TemplateError
from babel import dates
from odoo import models, fields, api, exceptions, _


class ResNotificationsetType(models.Model):
    _name = 'res.notificationset.type'
    _description = 'Type of notification set'
    _order = 'notificationsettype_code'

    SIZE_NAME = 50

    def _default_notificationsettype_code(self):
        resp = 0
        notificationsettypes = self.search(
            [], limit=1,
            order='notificationsettype_code desc')
        if notificationsettypes:
            resp = notificationsettypes[0].notificationsettype_code + 1
        else:
            resp = 1
        return resp

    def _default_iractreportxml_id(self):
        resp = 0
        try:
            resp = self.env.ref(
                'ncm_notifmgmt.action_res_notification_report').id
        except Exception:
            resp = 0
        return resp

    def _default_mailtemplate_id(self):
        resp = 0
        try:
            resp = self.env.ref(
                'ncm_notifmgmt.notificationset_type_standard_mail_template').id
        except Exception:
            resp = 0
        return resp

    def _default_main_page(self):
        resp = _(
            '<p><font style="font-size: 14px;">Basic sender and recipient '
            'data:</p><table class="table table-bordered"><tbody><tr><td><b>'
            'Company Name:</b></td><td>{{ company.notif_name }}</td><td><b>'
            'Contact Name:</b></td><td>{{ partner.notif_name }}</td></tr>'
            '<tr><td><b>Company Address 1/2:</b></td>'
            '<td>{{ company.notif_address_1 }}</td><td><b>'
            'Contact Address 1/2:</b></td><td>{{ partner.notif_address_1 }}'
            '</td></tr><tr><td><b>Company Address 2/2:</b></td>'
            '<td>{{ company.notif_address_2 }}</td><td><b>'
            'Contact Address 2/2:</b></td><td>{{ partner.notif_address_2 }}'
            '</td></tr><tr><td><b>Company Phone:</b></td><td>'
            '{{ company.notif_phone }}</td><td><b>Contact Phone:</b></td>'
            '<td>{{ partner.notif_phone }}</td></tr><tr><td><b>'
            'Company Email:</b></td><td>{{ company.notif_email }}</td>'
            '<td><b>Contact Email:</b></td><td>{{ partner.notif_email }}</td>'
            '</tr><tr><td><b>Company VAT:</b></td>'
            '<td>{{ company.notif_vat }}</td><td></td><td></td>'
            '</tr></tbody></table><p>(delete the excess data and write the '
            'text of the notification here)</p><p>{{ company.city }}, '
            '{{ current_day }} {{ current_month }} {{ current_year }}'
            '</font></p>')
        return resp

    def _get_mailtemplate_id_domain(self):
        valid_mailtemplate_ids = []
        try:
            valid_mailtemplates = self.env['mail.template'].search(
                [('model_id', '=',
                  self.env.ref('ncm_notifmgmt.model_res_notification').id)])
            if valid_mailtemplates:
                valid_mailtemplate_ids = valid_mailtemplates.ids
        except Exception:
            valid_mailtemplate_ids = []
        return [('id', 'in', valid_mailtemplate_ids)]

    notificationsettype_code = fields.Integer(
        string='Code',
        default=_default_notificationsettype_code,
        required=True,
        index=True,)

    name = fields.Char(
        string='Name',
        size=SIZE_NAME,
        required=True,
        translate=True,
        index=True,)

    main_page = fields.Html(
        string='Notification Template: main page',
        default=_default_main_page,
        translate=True,)

    final_paragraph = fields.Html(
        string='Notification Template: final paragraph',
        translate=True,)

    include_partner_if_customer = fields.Boolean(
        string='Include customers',
        default=True,)

    include_partner_if_supplier = fields.Boolean(
        string='Include suppliers',
        default=True,)

    include_partner_all = fields.Boolean(
        string='Include all partners',
        default=False,)

    iractreportxml_id = fields.Many2one(
        string='PDF Template for notifications',
        comodel_name='ir.actions.report.xml',
        required=True,
        default=_default_iractreportxml_id,
        domain=[('model', '=', 'res.notification'),
                ('report_type', '=', 'qweb-pdf')],)

    mailtemplate_id = fields.Many2one(
        string='Email Template for notifications',
        comodel_name='mail.template',
        required=True,
        default=_default_mailtemplate_id,
        domain=_get_mailtemplate_id_domain,)

    notes = fields.Html(
        string='Notes',
        translate=True,)

    is_standard = fields.Boolean(
        string='Standard Type (y/n)',
        default=False)

    notificationset_ids = fields.One2many(
        string='Notification Sets',
        comodel_name='res.notificationset',
        inverse_name='notificationset_type_id')

    number_of_notificationsets = fields.Integer(
        string='Number of notification sets',
        compute='_compute_number_of_notificationsets',)

    rendered_main_page = fields.Html(
        string='Notification Template: rendered main page',
        compute='_compute_rendered_main_page')

    rendered_final_paragraph = fields.Html(
        string='Notification Template: rendered final paragraph',
        compute='_compute_rendered_final_paragraph')

    _sql_constraints = [
        ('valid_notificationsettype_code',
         'CHECK (notificationsettype_code > 0)',
         'The notification set type code must be a positive value.'),
        ('unique_notificationsettype_code',
         'UNIQUE (notificationsettype_code)',
         'Existing notification set type.'),
        ]

    @api.multi
    def _compute_number_of_notificationsets(self):
        for record in self:
            number_of_notificationsets = 0
            if record.notificationset_ids:
                number_of_notificationsets = len(record.notificationset_ids)
            record.number_of_notificationsets = number_of_notificationsets

    @api.multi
    def _compute_rendered_main_page(self):
        for record in self:
            record.rendered_main_page = \
                record._get_rendered_text(record.main_page)

    @api.multi
    def _compute_rendered_final_paragraph(self):
        for record in self:
            record.rendered_final_paragraph = \
                record._get_rendered_text(record.final_paragraph)

    def _get_rendered_text(self, raw_text, ref_partner=None):
        if not ref_partner:
            ref_partner = self._get_a_partner()
        if (not raw_text) or (not ref_partner):
            return ''
        resp = ''
        lang = ref_partner.lang
        if not lang:
            lang = 'en_US'
        today = date.today()
        try:
            template = Template(raw_text)
            resp = template.render(
                partner=ref_partner,
                company=ref_partner.company_id.partner_id,
                current_day=dates.format_date(today, 'd', locale=lang),
                current_month=dates.format_date(today, 'LLLL', locale=lang),
                current_year=dates.format_date(today, 'y', locale=lang),)
        except TemplateError as e:
            resp = '<p style="text-align:center;color:red;">' + \
                '<b><font style="font-size: 14px;">' + \
                _('ERROR IN TEMPLATE') + '</font></b></p>' + \
                '<p><br>' + e.message + '</p>'
        return resp

    def _get_a_partner(self):
        resp = None
        conditions = []
        if (not self.include_partner_all):
            if self.include_partner_if_customer:
                conditions = [('customer', '=', True),
                              ('parent_id', '=', False),
                              ('partner_share', '=', True)]
            else:
                conditions = [('supplier', '=', True),
                              ('parent_id', '=', False),
                              ('partner_share', '=', True)]
        partners = self.env['res.partner'].search(conditions, order='name')
        if partners:
            number_of_partners = len(partners)
            epoch_time = int(time())
            partner_to_select = epoch_time % number_of_partners
            resp = partners[partner_to_select]
        return resp

    @api.constrains('include_partner_if_customer',
                    'include_partner_if_supplier',
                    'include_partner_all')
    def _check_include_partner_client_supplier(self):
        for record in self:
            if not self._is_marked_an_option(record):
                raise exceptions.UserError(_(
                    'Inclusion options: It is mandatory to choose at least '
                    'one option.'))
            if self._option_marked_if_all(record):
                raise exceptions.UserError(_(
                    'Inclusion options: It is not possible to choose all '
                    'contacts and other options.'))

    def _is_marked_an_option(self, record):
        resp = False
        if (record.include_partner_if_customer or
           record.include_partner_if_supplier or
           record.include_partner_all):
            resp = True
        return resp

    def _option_marked_if_all(self, record):
        resp = False
        if (record.include_partner_all and
            (record.include_partner_if_customer or
             record.include_partner_if_supplier)):
            resp = True
        return resp

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            display_name = record.name + \
                ' [' + str(record.notificationsettype_code) + ']'
            result.append((record.id, display_name))
        return result

    @api.multi
    def unlink(self):
        for record in self:
            if record.is_standard:
                raise exceptions.UserError(_('It is not possible to remove '
                                             'a \'STANDARD\' type of '
                                             'notification set.'))
        res = super(ResNotificationsetType, self).unlink()
        return res

    @api.multi
    def action_get_notificationsets(self):
        self.ensure_one()
        # Provisional
        print 'action_get_notificationsets'

    @api.multi
    def action_preview_rendered_notification(self):
        self.ensure_one()
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Notification Preview'),
            'res_model': 'wizard.preview.notification',
            'src_model': 'res.notificationset.type',
            'view_mode': 'form',
            'target': 'new',
            'context': {'current_model': 'res.notificationset.type'},
            }
        return act_window
