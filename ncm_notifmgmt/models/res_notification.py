# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from os import remove
from base64 import encodestring
from logging import getLogger
from odoo import models, fields, api, exceptions, _
from odoo.tools import config


class ResNotification(models.Model):
    _name = 'res.notification'
    _description = 'Notification'
    _inherit = 'mail.thread'
    _order = 'name'

    SIZE_NAME = 60

    notificationset_id = fields.Many2one(
        string='Notification Set',
        comodel_name='res.notificationset',
        required=True,
        index=True,
        ondelete='cascade',)

    partner_id = fields.Many2one(
        string='Contact',
        comodel_name='res.partner',
        required=True,
        index=True,
        ondelete='restrict',)

    name = fields.Char(
        string='Name',
        size=SIZE_NAME,
        required=True,
        index=True,)

    creation_date = fields.Date(
        string='Creation Date',
        store=True,
        index=True,
        compute='_compute_creation_date',)

    issue = fields.Char(
        string='Issue',
        store=True,
        index=True,
        compute='_compute_issue',)

    customer = fields.Boolean(
        string='Is a customer',
        store=True,
        index=True,
        compute='_compute_customer',)

    supplier = fields.Boolean(
        string='Is a supplier',
        store=True,
        index=True,
        compute='_compute_supplier',)

    internal_user = fields.Boolean(
        string='Is a internal user',
        store=True,
        index=True,
        compute='_compute_internal_user',)

    vat = fields.Char(
        string='TIN',
        store=True,
        index=True,
        compute='_compute_vat',)

    company_type = fields.Selection(
        selection=[
            ('person', 'Individual'),
            ('company', 'Company')],
        string='Company Type',
        store=True,
        index=True,
        compute='_compute_company_type',)

    parent_id = fields.Many2one(
        string='Related Company',
        comodel_name='res.partner',
        store=True,
        index=True,
        compute='_compute_parent_id',)

    with_parent_id = fields.Boolean(
        string='Has a parent (y/n)',
        store=True,
        compute='_compute_with_parent_id',)

    no_parent_id = fields.Char(
        string='Fixed message for no related company',
        compute='_compute_no_parent_id',)

    state = fields.Selection(
        selection=[
            ('01_draft', 'Draft'),
            ('02_generated', 'Generated'),
            ('03_sent', 'N. Sent'),
            ('04_executed', 'Executed'),
        ],
        string='State',
        default='01_draft',
        index=True,
        required=True,
        track_visibility='onchange',)

    main_page = fields.Html(
        string='Notification Template: main page',
        translate=True,)

    final_paragraph = fields.Html(
        string='Notification Template: final paragraph',
        translate=True,)

    notes = fields.Char(
        string='Notes',)

    selected = fields.Boolean(
        string='Selected (y/n)',
        default=True,)

    check_mark = fields.Char(
        string='Check-Mark for selected records',
        compute='_compute_check_mark',)

    document = fields.Binary(
        string='Notification (PDF)',
        attachment=True,)

    document_name = fields.Char(
        string='Document Name')

    rendered_main_page = fields.Html(
        string='Notification Template: rendered main page',
        compute='_compute_rendered_main_page')

    rendered_final_paragraph = fields.Html(
        string='Notification Template: rendered final paragraph',
        compute='_compute_rendered_final_paragraph')

    sent = fields.Boolean(
        string='Notification Sent',
        default=False,)

    envelope_mark = fields.Char(
        string='Envelope-Mark for notification sent',
        compute='_compute_envelope_mark',)

    email = fields.Char(
        string='Email',
        store=True,
        index=True,
        compute='_compute_email',)

    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
         'Existing Notification.'),
        ]

    @api.depends('notificationset_id', 'notificationset_id.creation_date')
    def _compute_creation_date(self):
        for record in self:
            creation_date = None
            if record.notificationset_id:
                creation_date = record.notificationset_id.creation_date
            record.creation_date = creation_date

    @api.depends('notificationset_id', 'notificationset_id.issue')
    def _compute_issue(self):
        for record in self:
            issue = ''
            if record.notificationset_id:
                issue = record.notificationset_id.issue
            record.issue = issue

    @api.depends('partner_id')
    def _compute_customer(self):
        for record in self:
            customer = False
            if (record.partner_id and record.partner_id.customer and
               (not record.partner_id.parent_id) and
               record.partner_id.partner_share):
                customer = True
            record.customer = customer

    @api.depends('partner_id')
    def _compute_supplier(self):
        for record in self:
            supplier = False
            if (record.partner_id and record.partner_id.supplier and
               (not record.partner_id.parent_id) and
               record.partner_id.partner_share):
                supplier = True
            record.supplier = supplier

    @api.depends('partner_id')
    def _compute_internal_user(self):
        for record in self:
            internal_user = False
            if (record.partner_id and (not record.partner_id.partner_share)):
                internal_user = True
            record.internal_user = internal_user

    @api.depends('partner_id', 'partner_id.vat')
    def _compute_vat(self):
        for record in self:
            vat = ''
            if record.partner_id and record.partner_id.vat:
                vat = record.partner_id.vat
            record.vat = vat

    @api.depends('partner_id', 'partner_id.company_type')
    def _compute_company_type(self):
        for record in self:
            company_type = ''
            if record.partner_id:
                company_type = record.partner_id.company_type
            record.company_type = company_type

    @api.depends('partner_id', 'partner_id.parent_id')
    def _compute_parent_id(self):
        for record in self:
            parent_id = None
            if record.partner_id and record.partner_id.parent_id:
                parent_id = record.partner_id.parent_id
            record.parent_id = parent_id

    @api.depends('parent_id')
    def _compute_with_parent_id(self):
        for record in self:
            with_parent_id = False
            if record.parent_id:
                with_parent_id = True
            record.with_parent_id = with_parent_id

    @api.multi
    def _compute_no_parent_id(self):
        for record in self:
            record.no_parent_id = _('The same')

    @api.multi
    def _compute_check_mark(self):
        for record in self:
            check_mark = ''
            if record.selected:
                check_mark = '✔'
            record.check_mark = check_mark

    @api.multi
    def _compute_rendered_main_page(self):
        for record in self:
            rendered_main_page = ''
            if (record.notificationset_id and
               record.notificationset_id.notificationset_type_id):
                notificationset_type = \
                    record.notificationset_id.notificationset_type_id
                rendered_main_page = \
                    notificationset_type._get_rendered_text(
                        record.main_page, ref_partner=record.partner_id)
            record.rendered_main_page = rendered_main_page

    @api.multi
    def _compute_rendered_final_paragraph(self):
        for record in self:
            rendered_final_paragraph = ''
            if (record.notificationset_id and
               record.notificationset_id.notificationset_type_id):
                notificationset_type = \
                    record.notificationset_id.notificationset_type_id
                rendered_final_paragraph = \
                    notificationset_type._get_rendered_text(
                        record.final_paragraph, ref_partner=record.partner_id)
            record.rendered_final_paragraph = rendered_final_paragraph

    @api.multi
    def _compute_envelope_mark(self):
        for record in self:
            envelope_mark = ''
            if record.sent:
                envelope_mark = '✉'
            record.envelope_mark = envelope_mark

    @api.depends('partner_id', 'partner_id.email')
    def _compute_email(self):
        for record in self:
            email = ''
            if record.partner_id and record.partner_id.email:
                email = record.partner_id.email
            record.email = email

    @api.constrains('state', 'selected')
    def _check_state_selected(self):
        for record in self:
            if (not record.selected and record.state != '01_draft'):
                raise exceptions.UserError(_(
                    'A notification that is not in a draft state must be '
                    'selected.'))

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            display_name = record.notificationset_id.name + \
                ' (' + record.partner_id.name + ')'
            result.append((record.id, display_name))
        return result

    @api.model
    def create(self, vals):
        if 'notificationset_id' in vals and vals['notificationset_id']:
            notificationset = self.env['res.notificationset'].browse(
                vals['notificationset_id'])
            if notificationset:
                vals['main_page'] = notificationset.main_page
                vals['final_paragraph'] = notificationset.final_paragraph
        return super(ResNotification, self).create(vals)

    @api.multi
    def write(self, vals):
        super(ResNotification, self).write(vals)
        if (len(self) == 1 and self.state != '01_draft' and
           ('main_page' in vals or 'final_paragraph' in vals)):
            report_name = 'ncm_notifmgmt.report_res_notification'
            notificationset_type = \
                self.notificationset_id.notificationset_type_id
            if notificationset_type.iractreportxml_id:
                report_name = \
                    notificationset_type.iractreportxml_id.report_name
            pdf = self.env['report'].with_context(
                {'lang': self.partner_id.lang}).get_pdf(
                    [self.id], report_name)
            if pdf:
                self.delete_attachment()
                vals['document'] = encodestring(pdf)
                super(ResNotification, self).write(vals)
        return True

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(ResNotification, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        actions_to_remove = []
        if (res['name'] == 'res.notification.view.form' or
           res['name'] == 'res.notification.view.tree'):
            actions_to_remove = \
                ['ncm_notifmgmt.set_selected_true',
                 'ncm_notifmgmt.set_selected_false',
                 'ncm_notifmgmt.multiple_mailing']
        if (res['name'] == 'res.notification.draft.view.tree'):
            actions_to_remove = \
                ['ncm_notifmgmt.multiple_mailing']
        if (res['name'] == 'res.notification.generated.view.tree'):
            actions_to_remove = \
                ['ncm_notifmgmt.set_selected_true',
                 'ncm_notifmgmt.set_selected_false']
        if (res['name'] == 'res.notification.particular.view.tree'):
            actions_to_remove = \
                ['ncm_notifmgmt.set_selected_true',
                 'ncm_notifmgmt.set_selected_false',
                 'ncm_notifmgmt.multiple_mailing']
        if actions_to_remove:
            actions = res['toolbar']['action']
            new_actions = []
            for action in actions:
                if action['xml_id'] not in actions_to_remove:
                    new_actions.append(action)
            res['toolbar']['action'] = new_actions
        return res

    @api.multi
    def set_selected(self, ref_value=True):
        for record in self:
            if record.state == '01_draft':
                record.write({'selected': ref_value})

    @api.multi
    def delete_attachment(self):
        base_path = config.filestore(self._cr.dbname)
        if base_path and len(base_path) >= 1:
            if base_path[-1:] != '/':
                base_path = base_path + '/'
        if base_path:
            for record in self:
                self.env.cr.execute(
                    """
                    SELECT store_fname FROM ir_attachment
                    WHERE res_model='res.notification' AND res_id=
                    """ + str(record.id))
                query_results = self.env.cr.dictfetchall()
                for row in (query_results or []):
                    attachment_to_delete = base_path + row.get('store_fname')
                    try:
                        remove(attachment_to_delete)
                    except Exception:
                        pass

    @api.multi
    def action_send_notification(self):
        self.ensure_one()
        if (self.state != '01_draft' or self.state != '04_executed'):
            mail_ok = self._send_mail()
            if not mail_ok:
                raise exceptions.UserError(
                    _('ATTENTION: The mail could not be sent.'))
            if (self.state != '03_sent' or not self.sent):
                vals = {}
                if self.state != '03_sent':
                    vals.update({'state': '03_sent'})
                if not self.sent:
                    vals.update({'sent': True})
                self.write(vals)

    @api.multi
    def _send_mail(self):
        resp = True
        _logger = getLogger(self.__class__.__name__)
        for record in self:
            notification = record
            mailtemplate = None
            if (notification.partner_id and
               notification.notificationset_id and
               notification.notificationset_id.notificationset_type_id):
                notificationset_type = \
                    notification.notificationset_id.notificationset_type_id
                mailtemplate = notificationset_type.mailtemplate_id
            if mailtemplate:
                preffix_message = _('Mail for notification') + ' ' + \
                    notification.name + ', ' + \
                    _('for the partner') + ' \"' + \
                    notification.partner_id.name + '\": '
                suffix_message = _('sent successfully')
                send_ok = True
                try:
                    if notification.partner_id.email:
                        mailtemplate.send_mail(notification.id,
                                               force_send=True)
                    else:
                        send_ok = False
                except Exception:
                    send_ok = False
                if not send_ok:
                    resp = False
                    suffix_message = _('send error')
                _logger.info(preffix_message + suffix_message)
        return resp

    @api.multi
    def action_send_notifications(self):
        for record in self:
            if (record.state == '02_generated' or record.state == '03_sent'):
                mail_ok = record._send_mail()
                if mail_ok and (record.state != '03_sent' or not record.sent):
                    vals = {}
                    if record.state != '03_sent':
                        vals.update({'state': '03_sent'})
                    if not record.sent:
                        vals.update({'sent': True})
                    record.write(vals)
