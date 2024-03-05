# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import threading
import odoo
from logging import getLogger
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

    def _default_background_process(self):
        resp = False
        background_process = self.env['ir.values'].get_default(
            'res.notif.config.settings', 'background_process')
        if background_process:
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
            ('02_inprogress', 'In progress'),
            ('03_validated', 'Validated'),
            ('04_closed', 'Closed'),
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

    number_of_selected_notifications_for_draft_state = fields.Integer(
        string='Number of selected notifications (draft state)',
        compute='_compute_number_of_selected_notifications_for_draft_state',)

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

    background_process = fields.Boolean(
        string='Create background notifications',
        default=_default_background_process,)

    inprogress_substate = fields.Selection(
        selection=[
            ('01_halted', 'Halted'),
            ('02_running', 'Running'),
            ('03_paused', 'Paused'),
        ],
        string='Substate for in-progress',
        default='01_halted',)

    progress_percentage = fields.Integer(
        string='Progress Percentage',
        compute='_compute_progress_percentage',)

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
            self.env.cr.execute("""
                SELECT COUNT(*) FROM res_notification
                WHERE notificationset_id=%s""", (record.id,))
            query_results = self.env.cr.dictfetchall()
            if query_results and query_results[0].get('count') is not None:
                number_of_notifications = query_results[0].get('count')
            record.number_of_notifications = number_of_notifications

    @api.multi
    def _compute_number_of_selected_notifications(self):
        for record in self:
            number_of_selected_notifications = 0
            self.env.cr.execute("""
                SELECT COUNT(*) FROM res_notification
                WHERE notificationset_id=%s
                AND selected""", (record.id,))
            query_results = self.env.cr.dictfetchall()
            if query_results and query_results[0].get('count') is not None:
                number_of_selected_notifications = \
                    query_results[0].get('count')
            record.number_of_selected_notifications = \
                number_of_selected_notifications

    @api.multi
    def _compute_number_of_selected_notifications_for_draft_state(self):
        for record in self:
            record.number_of_selected_notifications_for_draft_state = \
                record.number_of_selected_notifications

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
            self.env.cr.execute("""
                SELECT COUNT(*) FROM res_notification
                WHERE notificationset_id=%s
                AND state != '01_draft'
                AND selected AND sent""", (record.id,))
            query_results = self.env.cr.dictfetchall()
            if query_results and query_results[0].get('count') is not None:
                number_of_notifications_sent = query_results[0].get('count')
            record.number_of_notifications_sent = number_of_notifications_sent

    @api.multi
    def _compute_number_of_notifications_not_sent(self):
        for record in self:
            record.number_of_notifications_not_sent = \
                (record.number_of_selected_notifications -
                 record.number_of_notifications_sent)

    @api.multi
    def _compute_progress_percentage(self):
        for record in self:
            progress_percentage = 0
            if (record.state == '03_validated' or record.state == '04_closed'):
                progress_percentage = 100
            else:
                if record.state == '02_inprogress':
                    number_of_selected_notifications = \
                        record.number_of_selected_notifications
                    if number_of_selected_notifications > 0:
                        number_of_generated_notifications = 0
                        self.env.cr.execute("""
                            SELECT COUNT(*) FROM res_notification
                            WHERE notificationset_id=%s
                            AND state = '02_generated'""", (record.id,))
                        query_results = self.env.cr.dictfetchall()
                        if query_results and query_results[0].get('count') is not None:
                            number_of_generated_notifications = \
                                query_results[0].get('count')
                        progress_percentage = (int(round(100*(float(
                            number_of_generated_notifications) /
                            float(number_of_selected_notifications)))))
            record.progress_percentage = progress_percentage

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
    def generate_notifications_orm(self):
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
    def generate_notifications(self):
        for notificationset in self:
            if notificationset.notification_ids:
                notificationset.notification_ids.unlink()
            sql_statement = \
                notificationset._generate_notifications_get_sql_statement()
            if sql_statement:
                self.env.cr.execute(sql_statement)
                self.env.cr.commit()
                self.env.invalidate_all()
                self._gn_final_process(notificationset)

    @api.multi
    def _generate_notifications_get_sql_statement(self):
        self.ensure_one()
        user_id = self.env.user.id
        main_page = ''
        final_paragraph = ''
        if self.main_page:
            main_page = self.main_page.replace("'", "''")
        if self.final_paragraph:
            final_paragraph = self.final_paragraph.replace("'", "''")
        selected_by_default = self.env['ir.values']. \
            get_default('res.notif.config.settings',
                        'selected_by_default')
        if selected_by_default:
            selected = 'true'
        else:
            selected = 'false'
        resp = 'INSERT INTO res_notification (id, create_uid, write_uid, ' + \
            'create_date, write_date, notificationset_id, partner_id, ' + \
            'name, creation_date, issue, customer, supplier, ' + \
            'internal_user, ' + self._gn_get_additional_fields() + \
            'vat, company_type, parent_id, state, main_page, ' + \
            'final_paragraph, selected, sent, email) ' + \
            'SELECT NEXTVAL(\'res_notification_id_seq\'), %s, %s, ' + \
            'now(), now(), %s, rp.id, \'%s-\' ' + \
            '|| LPAD(ROW_NUMBER() OVER (ORDER BY NAME)::TEXT, 6, \'0\'), ' + \
            '\'%s\', \'%s\', rp.customer, rp.supplier, ' + \
            'NOT rp.partner_share, ' + \
            self._gn_get_additional_values() + 'rp.vat, ' + \
            '(CASE WHEN rp.is_company ' + \
            'THEN \'company\' ELSE \'person\' END), ' + \
            'rp.parent_id, \'01_draft\', \'%s\', \'%s\', ' + \
            selected + ', false, ' + \
            'rp.email ' + \
            'FROM res_partner rp ' + \
            self._gn_get_where_clause(self.notificationset_type_id) + \
            'ORDER BY rp.name'
        resp = resp % (user_id, user_id, self.id, self.name,
                       self.creation_date, self.issue,
                       main_page, final_paragraph)
        return resp

    # Hook
    def _gn_get_additional_fields(self):
        return ''

    # Hook
    def _gn_get_additional_values(self):
        return ''

    def _gn_get_where_clause(self, notificationset_type):
        resp = 'WHERE active '
        if (notificationset_type and
           (not notificationset_type.include_partner_all)):
            or_condition = self._gm_get_where_clause_or_condition(
                notificationset_type)
            if or_condition:
                resp = resp + 'AND (parent_id IS NULL) AND (' + \
                    or_condition + ') '
        return resp

    # Hook
    def _gm_get_where_clause_or_condition(self, notificationset_type):
        resp = ''
        if (notificationset_type.include_partner_if_customer and
           notificationset_type.include_partner_if_supplier):
            resp = 'rp.customer OR rp.supplier'
        else:
            if notificationset_type.include_partner_if_customer:
                resp = 'rp.customer'
            if notificationset_type.include_partner_if_supplier:
                resp = 'rp.supplier'
        return resp

    # Hook
    def _gn_final_process(self, notificationset):
        pass

    @api.multi
    def write(self, vals):
        super(ResNotificationset, self).write(vals)
        if len(self) == 1:
            return True
            if (self.notification_ids and
               ('main_page' in vals or 'final_paragraph' in vals)):
                sql_statement = 'UPDATE res_notification SET '
                if 'main_page' in vals:
                    sql_statement = \
                        sql_statement + 'main_page = \'' + \
                        vals['main_page'].replace("'", "''") + '\', '
                if 'final_paragraph' in vals:
                    sql_statement = \
                        sql_statement + 'final_paragraph = \'' + \
                        vals['final_paragraph'].replace("'", "''") + '\', '
                sql_statement = sql_statement[:-2] + \
                    ' WHERE notificationset_id = ' + str(self.id)
                self.env.cr.execute(sql_statement)
                self.env.cr.commit()
                self.env.invalidate_all()
        return True

    @api.multi
    def update_notifications(self, main_page, final_paragraph):
        for current_notification in self:
            if ((main_page or final_paragraph) and
               current_notification.notification_ids):
                # Provisional
                pass

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
    def action_go_to_state_03_validated(self):
        self.ensure_one()
        if (not ((self.state == '01_draft') or
                 (self.state == '02_inprogress' and
                  self.inprogress_substate == '03_paused'))):
            raise exceptions.UserError(_('This set is already validated, '
                                         'or it is in progress '
                                         '(maybe another user just validated '
                                         'it now).'))
        self.write({'state': '02_inprogress'})
        self.env.cr.execute(
            'UPDATE res_notificationset ' +
            'SET inprogress_substate = \'02_running\' ' +
            'WHERE id = ' + str(self.id))
        self.env.cr.commit()
        self.env.invalidate_all()
        if self.background_process:
            background_process = threading.Thread(
                target=self.generate_pdfs_background, args=(self.id,))
            background_process.start()
        else:
            self.generate_pdfs()

    @api.model
    def generate_pdfs_background(self, notificationset_id):
        with api.Environment.manage():
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                new_env = \
                    api.Environment(new_cr, self.env.uid, self.env.context)
                ns = new_env['res.notificationset'].browse(notificationset_id)
                if ns:
                    stop_process = False
                    if ns.notification_ids:
                        _logger = getLogger(self.__class__.__name__)
                        report_name = 'ncm_notifmgmt.report_res_notification'
                        if ns.notificationset_type_id.iractreportxml_id:
                            actreport = \
                                ns.notificationset_type_id.iractreportxml_id
                            report_name = actreport.report_name
                        remove_unselected = False
                        new_env.cr.execute(
                            'UPDATE res_notificationset ' +
                            'SET state = \'02_inprogress\' ,' +
                            'inprogress_substate = \'02_running\' ' +
                            'WHERE id = ' + str(ns.id))
                        new_env.cr.commit()
                        new_env.invalidate_all()
                        # PDF Generation
                        for n in ns.notification_ids:
                            if ns.inprogress_substate == '03_paused':
                                stop_process = True
                                break
                            if (n.selected and (not n.document)):
                                remove_unselected = True
                                preffix_message = _('PDF of notification') + \
                                    ' ' + n.name + '... '
                                suffix_message = _('generated')
                                try:
                                    pdf = new_env['report'].with_context(
                                        {'lang': n.partner_id.lang}).get_pdf(
                                            [n.id], report_name)
                                    if pdf:
                                        new_env.cr.execute(
                                            'UPDATE res_notification ' +
                                            'SET state = \'02_generated\' '
                                            'WHERE id = ' + str(n.id))
                                        new_env.cr.commit()
                                        new_env.invalidate_all()
                                        n.write({
                                            'document': encodestring(pdf),
                                            'document_name': n.name + '.pdf'
                                            })
                                except Exception:
                                    suffix_message = _('FAIL!')
                                _logger.info(preffix_message + suffix_message)
                        # Remove unselected notifications from set
                        if remove_unselected and (not stop_process):
                            new_env.cr.execute(
                                'DELETE FROM res_notification ' +
                                'WHERE notificationset_id = ' +
                                str(ns.id) + ' AND NOT selected')
                            new_env.cr.commit()
                            new_env.invalidate_all()
                    if (not stop_process):
                        ns.write({'state': '03_validated',
                                  'inprogress_substate': '01_halted'})

    @api.multi
    def generate_pdfs(self):
        for ns in self:
            stop_process = False
            if ns.notification_ids:
                _logger = getLogger(self.__class__.__name__)
                report_name = 'ncm_notifmgmt.report_res_notification'
                if ns.notificationset_type_id.iractreportxml_id:
                    actreport = ns.notificationset_type_id.iractreportxml_id
                    report_name = actreport.report_name
                remove_unselected = False
                self.env.cr.execute(
                    'UPDATE res_notificationset ' +
                    'SET state = \'02_inprogress\' ,' +
                    'inprogress_substate = \'02_running\' ' +
                    'WHERE id = ' + str(ns.id))
                self.env.cr.commit()
                self.env.invalidate_all()
                # PDF Generation
                for n in ns.notification_ids:
                    if ns.inprogress_substate == '03_paused':
                        stop_process = True
                        break
                    if (n.selected and (not n.document)):
                        remove_unselected = True
                        preffix_message = _('PDF of notification') + \
                            ' ' + n.name + '... '
                        suffix_message = _('generated')
                        try:
                            pdf = self.env['report'].with_context(
                                {'lang': n.partner_id.lang}).get_pdf(
                                    [n.id], report_name)
                            if pdf:
                                self.env.cr.execute(
                                    'UPDATE res_notification ' +
                                    'SET state = \'02_generated\' '
                                    'WHERE id = ' + str(n.id))
                                self.env.cr.commit()
                                self.env.invalidate_all()
                                n.write({
                                    'document': encodestring(pdf),
                                    'document_name': n.name + '.pdf'
                                    })
                        except Exception:
                            suffix_message = _('FAIL')
                        _logger.info(preffix_message + suffix_message)
                # Remove unselected notifications from set
                if remove_unselected and (not stop_process):
                    self.env.cr.execute(
                        'DELETE FROM res_notification ' +
                        'WHERE notificationset_id = ' +
                        str(ns.id) + ' AND NOT selected')
                    self.env.cr.commit()
                    self.env.invalidate_all()
            if (not stop_process):
                ns.write({'state': '03_validated',
                          'inprogress_substate': '01_halted'})

    @api.model
    def create_notification_pdfs(self):
        ns_in_draft_state = self.env['res.notificationset'].search(
            [('state', '=', '01_draft')])
        if ns_in_draft_state:
            ns_in_draft_state.generate_pdfs()

    @api.multi
    def action_return_to_state_01_draft(self):
        self.ensure_one()
        self.write({'state': '01_draft'})
        self.notification_ids.delete_attachment()
        self.generate_notifications()

    @api.multi
    def action_go_to_state_04_closed(self):
        self.ensure_one()
        self.write({'state': '04_closed'})
        if self.notification_ids:
            for notification in self.notification_ids:
                if notification.state != '01_draft':
                    notification.write({'state': '04_executed'})

    @api.multi
    def action_return_to_state_03_validated(self):
        self.ensure_one()
        self.write({'state': '03_validated'})
        if self.notification_ids:
            for notification in self.notification_ids:
                if notification.state == '04_executed':
                    if notification.sent:
                        notification.write({'state': '03_sent'})
                    else:
                        notification.write({'state': '02_generated'})

    @api.multi
    def action_go_to_substate_03_paused(self):
        self.ensure_one()
        if (not(self.state == '02_inprogress' and
                self.inprogress_substate == '02_running')):
            raise exceptions.UserError(_('The PDF generation process is no '
                                         'longer running.'))
        self.env.cr.execute(
            'UPDATE res_notificationset ' +
            'SET inprogress_substate = \'03_paused\' ' +
            'WHERE id = ' + str(self.id))
        self.env.cr.commit()
        self.env.invalidate_all()

    @api.multi
    def action_resume_pdf_generation(self):
        self.ensure_one()
        if (not(self.state == '02_inprogress' and
                self.inprogress_substate == '03_paused')):
            raise exceptions.UserError(_('The PDF generation process is '
                                         'running again, has finished, or '
                                         'has been cancelled.'))
        self.action_go_to_state_03_validated()

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
