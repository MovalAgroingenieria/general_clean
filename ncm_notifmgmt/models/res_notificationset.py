# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import encodestring
from odoo import models, fields, api, exceptions, _


class ResNotificationset(models.Model):
    _name = 'res.notificationset'
    _description = 'Notification Set'
    _inherit = 'mail.thread'
    _order = 'name'

    SIZE_NAME = 50
    SIZE_ISSUE = 100
    SIZE_SUFFIX = 6

    def _default_notificationset_type_id(self):
        resp = None
        default_notificationset_type_id = self.env['ir.values'].get_default(
            'res.notif.config.settings', 'default_notificationset_type_id')
        if default_notificationset_type_id:
            resp = default_notificationset_type_id
        return resp

    def _default_setted_sequence(self):
        resp = False
        sequence_notificationset_code_id = self.env['ir.values'].get_default(
            'res.notif.config.settings', 'sequence_notificationset_code_id')
        if sequence_notificationset_code_id:
            resp = True
        return resp

    name = fields.Char(
        string='Code',
        size=SIZE_NAME,
        index=True,)

    creation_date = fields.Date(
        string='Creation Date',
        default=lambda self: fields.datetime.now(),
        required=True,
        index=True,)

    issue = fields.Char(
        string='Issue',
        size=SIZE_ISSUE,
        required=True,
        index=True,)

    notificationset_type_id = fields.Many2one(
        string='Type of notification set',
        comodel_name='res.notificationset.type',
        default=_default_notificationset_type_id,
        required=True,
        index=True,)

    setted_sequence = fields.Boolean(
        string='Setted Sequence (y/n)',
        default=_default_setted_sequence,
        compute='_compute_setted_sequence',)

    state = fields.Selection(
        selection=[
            ('01_draft', 'Draft'),
            ('02_validated', 'Validated'),
            ('03_closed', 'Closed'),
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

    notes = fields.Html(
        string='Notes',
        translate=True,)

    notification_ids = fields.One2many(
        string='Notifications',
        comodel_name='res.notification',
        inverse_name='notificationset_id')

    number_of_notifications = fields.Integer(
        string='Number of notifications',
        compute='_compute_number_of_notifications',)

    number_of_selected_notifications = fields.Integer(
        string='Number of selected notifications',
        compute='_compute_number_of_selected_notifications',)

    rendered_main_page = fields.Html(
        string='Notification Template: rendered main page',
        compute='_compute_rendered_main_page')

    rendered_final_paragraph = fields.Html(
        string='Notification Template: rendered final paragraph',
        compute='_compute_rendered_final_paragraph')

    number_of_notifications_sent = fields.Integer(
        string='Number of notifications sent',
        compute='_compute_number_of_notifications_sent',)

    number_of_notifications_not_sent = fields.Integer(
        string='Number of notifications not sent',
        compute='_compute_number_of_notifications_not_sent',)

    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
         'Existing Notification Set.'),
        ]

    @api.multi
    def _compute_setted_sequence(self):
        sequence_notificationset_code_id = self.env['ir.values'].get_default(
            'res.notif.config.settings', 'sequence_notificationset_code_id')
        for record in self:
            setted_sequence = False
            if sequence_notificationset_code_id:
                setted_sequence = True
            record.setted_sequence = setted_sequence

    @api.multi
    def _compute_number_of_notifications(self):
        for record in self:
            number_of_notifications = 0
            if record.notification_ids:
                number_of_notifications = len(record.notification_ids)
            record.number_of_notifications = number_of_notifications

    @api.multi
    def _compute_number_of_selected_notifications(self):
        for record in self:
            number_of_selected_notifications = 0
            if record.notification_ids:
                for notification in record.notification_ids:
                    if (notification.selected and
                       notification.state != '01_draft'):
                        number_of_selected_notifications = \
                            number_of_selected_notifications + 1
            record.number_of_selected_notifications = \
                number_of_selected_notifications

    @api.multi
    def _compute_rendered_main_page(self):
        for record in self:
            rendered_main_page = ''
            if record.notificationset_type_id:
                rendered_main_page = \
                    record.notificationset_type_id._get_rendered_text(
                        record.main_page)
            record.rendered_main_page = rendered_main_page

    @api.multi
    def _compute_rendered_final_paragraph(self):
        for record in self:
            rendered_final_paragraph = ''
            if record.notificationset_type_id:
                rendered_final_paragraph = \
                    record.notificationset_type_id._get_rendered_text(
                        record.final_paragraph)
            record.rendered_final_paragraph = rendered_final_paragraph

    @api.multi
    def _compute_number_of_notifications_sent(self):
        for record in self:
            number_of_notifications_sent = 0
            if record.notification_ids:
                for notification in record.notification_ids:
                    if (notification.selected and notification.sent and
                       notification.state != '01_draft'):
                        number_of_notifications_sent = \
                            number_of_notifications_sent + 1
            record.number_of_notifications_sent = \
                number_of_notifications_sent

    @api.multi
    def _compute_number_of_notifications_not_sent(self):
        for record in self:
            record.number_of_notifications_not_sent = \
                (record.number_of_selected_notifications -
                 record.number_of_notifications_sent)

    @api.onchange('notificationset_type_id')
    def _onchange_notificationset_type_id(self):
        if self.notificationset_type_id:
            self.main_page = self.notificationset_type_id.main_page
            self.final_paragraph = self.notificationset_type_id.final_paragraph

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            display_name = record.name + \
                ' (' + record.issue + ')'
            result.append((record.id, display_name))
        return result

    @api.model
    def create(self, vals):
        sequence_notificationset_code_id = self.env['ir.values'].get_default(
            'res.notif.config.settings', 'sequence_notificationset_code_id')
        if sequence_notificationset_code_id:
            model_ir_sequence = self.env['ir.sequence'].sudo()
            sequence_notificationset_code = \
                model_ir_sequence.browse(sequence_notificationset_code_id)
            if sequence_notificationset_code:
                new_code = model_ir_sequence.next_by_code(
                    sequence_notificationset_code.code)
                vals['name'] = new_code
        else:
            if 'name' in vals and vals['name']:
                vals['name'] = vals['name'].strip()
        if (('name' not in vals) or (not vals['name'])):
            raise exceptions.ValidationError(_('It is mandatory to enter a '
                                               'code for the new notification '
                                               'set.'))
        new_notificationset = super(ResNotificationset, self).create(vals)
        new_notificationset.generate_notifications()
        return new_notificationset

    @api.multi
    def generate_notifications(self):
        new_notifications = []
        model_res_notification = self.env['res.notification']
        model_res_partner = self.env['res.partner']
        for current_notificationset in self:
            previous_notifications = model_res_notification.search([
                ('notificationset_id', '=', current_notificationset.id)])
            if previous_notifications:
                previous_notifications.unlink()
            conditions = \
                current_notificationset._get_conditions_for_new_notifications()
            if conditions:
                num_conditions = len(conditions)
                if num_conditions > 1:
                    i = 1
                    new_conditions = []
                    for condition in conditions:
                        if i < num_conditions:
                            new_conditions.append('|')
                        new_conditions.append(condition)
                        i = i + 1
                    conditions = new_conditions
                conditions.insert(0, ('parent_id', '=', False))
                conditions.insert(0, ('partner_share', '=', True))
            partners_to_add = model_res_partner.search(conditions,
                                                       order='display_name')
            if partners_to_add:
                i = 1
                for partner in partners_to_add:
                    vals = \
                        current_notificationset._get_values_of_new_notification(
                            partner, i)
                    new_notification = model_res_notification.create(vals)
                    new_notifications.append(new_notification)
                    i = i + 1
        return new_notifications

    @api.multi
    def _get_conditions_for_new_notifications(self):
        self.ensure_one()
        resp = []
        if self.notificationset_type_id:
            if not self.notificationset_type_id.include_partner_all:
                if self.notificationset_type_id.include_partner_if_customer:
                    resp.append(('customer', '=', True))
                if self.notificationset_type_id.include_partner_if_supplier:
                    resp.append(('supplier', '=', True))
        return resp

    @api.multi
    def _get_values_of_new_notification(self, partner, pos):
        self.ensure_one()
        vals = {}
        vals.update({'notificationset_id': self.id})
        vals.update({'partner_id': partner.id})
        vals.update({'name': self.name + '-' +
                     str(pos).zfill(self.SIZE_SUFFIX)})
        return vals

    @api.multi
    def write(self, vals):
        if (len(self) == 1 and self.notification_ids and
           ('main_page' in vals or 'final_paragraph' in vals)):
            vals_for_notifications = {}
            if 'main_page' in vals:
                vals_for_notifications.update(
                    {'main_page': vals['main_page']})
            if 'final_paragraph' in vals:
                vals_for_notifications.update(
                    {'final_paragraph': vals['final_paragraph']})
            for notification in self.notification_ids:
                notification.write(vals_for_notifications)
        super(ResNotificationset, self).write(vals)
        return True

    @api.multi
    def unlink(self):
        for record in self:
            if record.notification_ids:
                record.notification_ids.delete_attachment()
                record.notification_ids.unlink()
        res = super(ResNotificationset, self).unlink()
        return res

    @api.multi
    def action_preview_rendered_notification(self):
        self.ensure_one()
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Notification Preview'),
            'res_model': 'wizard.preview.notification',
            'src_model': 'res.notificationset',
            'view_mode': 'form',
            'target': 'new',
            'context': {'current_model': 'res.notificationset'},
            }
        return act_window

    @api.multi
    def action_go_to_state_02_validated(self):
        self.ensure_one()
        self.write({'state': '02_validated'})
        if self.notification_ids:
            report_name = 'ncm_notifmgmt.report_res_notification'
            if self.notificationset_type_id.iractreportxml_id:
                report_name = \
                    self.notificationset_type_id.iractreportxml_id.report_name
            for notification in self.notification_ids:
                if notification.selected:
                    pdf = self.env['report'].with_context(
                        {'lang': notification.partner_id.lang}).get_pdf(
                            [notification.id], report_name)
                    if pdf:
                        notification.write({
                            'state': '02_generated',
                            'document': encodestring(pdf),
                            'document_name': notification.name + '.pdf'
                            })
                else:
                    notification.unlink()

    @api.multi
    def action_return_to_state_01_draft(self):
        self.ensure_one()
        self.write({'state': '01_draft'})
        if self.notification_ids:
            self.notification_ids.delete_attachment()
            self.generate_notifications()

    @api.multi
    def action_go_to_state_03_closed(self):
        self.ensure_one()
        self.write({'state': '03_closed'})
        if self.notification_ids:
            for notification in self.notification_ids:
                if notification.state != '01_draft':
                    notification.write({'state': '04_executed'})

    @api.multi
    def action_return_to_state_02_validated(self):
        self.ensure_one()
        self.write({'state': '02_validated'})
        if self.notification_ids:
            for notification in self.notification_ids:
                if notification.state == '04_executed':
                    if notification.sent:
                        notification.write({'state': '03_sent'})
                    else:
                        notification.write({'state': '02_generated'})

    @api.multi
    def action_get_notifications(self):
        self.ensure_one()
        current_notificationset = self
        id_tree_view = self.env.ref(
            'ncm_notifmgmt.res_notification_draft_view_tree').id
        search_view = self.env.ref(
            'ncm_notifmgmt.res_notification_draft_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Selection of partners for notifications'),
            'res_model': 'res.notification',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree')],
            'search_view_id': [search_view.id],
            'target': 'current',
            'domain': [('notificationset_id', '=', current_notificationset.id)],
            }
        return act_window

    @api.multi
    def action_get_selected_notifications(self):
        self.ensure_one()
        current_notificationset = self
        id_tree_view = self.env.ref(
            'ncm_notifmgmt.res_notification_generated_view_tree').id
        id_form_view = self.env.ref(
            'ncm_notifmgmt.res_notification_view_form').id
        search_view = self.env.ref(
            'ncm_notifmgmt.res_notification_generated_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Notifications'),
            'res_model': 'res.notification',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'views': [(id_tree_view, 'tree'), (id_form_view, 'form')],
            'search_view_id': [search_view.id],
            'target': 'current',
            'domain': [('notificationset_id', '=', current_notificationset.id),
                       ('selected', '=', True),
                       ('state', '!=', '01_draft')],
            }
        return act_window

    @api.multi
    def action_send_all_notifications(self):
        self.ensure_one()
        self.notification_ids.action_send_notifications()
