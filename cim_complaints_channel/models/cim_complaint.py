# -*- coding: utf-8 -*-
# Copyright 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from odoo import models, fields, api, exceptions, _


class CimComplaint(models.Model):
    _name = 'cim.complaint'
    _description = 'Complaint'
    _inherit = 'mail.thread'
    _order = 'name'

    SIZE_SMALL = 25
    SIZE_MEDIUM = 50
    SIZE_MEDIUM_EXTRA = 75
    SIZE_NORMAL = 100

    def _default_setted_sequence(self):
        resp = False
        sequence_complaint_code_id = self.env['ir.values'].get_default(
            'res.cim.config.settings', 'sequence_complaint_code_id')
        if sequence_complaint_code_id:
            resp = True
        return resp

    name = fields.Char(
        string='Code',
        size=SIZE_SMALL,
        index=True,)

    issue = fields.Char(
        string='Issue',
        size=SIZE_MEDIUM_EXTRA,
        required=True,
        index=True,)

    description = fields.Text(
        string='Facts denounced',
        required=True,
        index=True,)

    tracking_code = fields.Char(
        string='Tracking Code',
        size=SIZE_SMALL,
        index=True,
        readonly=True,)

    complaint_type_id = fields.Many2one(
        string='Complaint Type',
        comodel_name='cim.complaint.type',
        required=True,
        index=True,
        ondelete='restrict',)

    defendant_name = fields.Char(
        string='Defendant Name',
        size=SIZE_NORMAL,
        index=True,)

    witness_name = fields.Text(
        string='Witnesses',
        index=True,)

    is_complainant_involved = fields.Boolean(
        string='Complainant involved',
        default=False,
        required=True,)

    link_type_id = fields.Many2one(
        string='Link Type',
        comodel_name='cim.link.type',
        required=True,
        index=True,
        ondelete='restrict',)

    complaint_frequency = fields.Selection(
        string="Complaint Frequency",
        selection=[
            ('01_not_remembered', 'Not remembered'),
            ('02_specific_day', 'A specific day'),
            ('03_continuously', 'Continuously'),
        ],
        default='01_not_remembered',
        required=True,
        index=True,)

    complaint_time = fields.Datetime(
        string='Complaint Time',)

    complaint_date = fields.Date(
        string='Complaint Date',
        store=True,
        index=True,
        compute='_compute_complaint_date',)

    creation_date = fields.Date(
        string='Creation Date',
        default=lambda self: fields.datetime.now(),)

    complainant_email = fields.Char(
        string='Complainant E-mail',
        size=SIZE_MEDIUM,
        index=True,
        track_visibility='onchange',)

    complainant_name = fields.Char(
        string='Complainant Name',
        size=SIZE_NORMAL,
        index=True,)

    complainant_vat = fields.Char(
        string='Complainant VAT',
        size=SIZE_SMALL,
        index=True,)

    complainant_phone = fields.Char(
        string='Complainant Phone',
        size=SIZE_SMALL,
        index=True,)

    is_anonymous = fields.Boolean(
        string='Anonymous Complaint',
        default=True,
        compute='_compute_is_anonymous')

    measures_taken = fields.Text(
        string='Measures taken',
        index=True,)

    resolution_text = fields.Text(
        string='Resolution Text',)

    user_in_group_cim_settings = fields.Boolean(
        string='Is a complaints administrator?',
        compute='_compute_user_in_group_cim_settings',)

    is_delegated = fields.Boolean(
        string='Delegated Complaint',
        default=False,
        readonly=True,)

    notes = fields.Html(
        string='Notes',)

    state = fields.Selection(
        string="State",
        selection=[
            ('01_received',
             'Received'),
            ('02_admitted',
             'Admitted'),
            ('03_in_progress',
             'In progress'),
            ('04_ready',
             'Ready'),
            ('05_resolved',
             'Resolved'),
        ],
        default='01_received',
        required=True,
        index=True,
        track_visibility='onchange',)

    investigating_user_id = fields.Many2one(
        string='Instructor',
        comodel_name='res.users',
        store=True,
        compute='_compute_investigating_user_id',
        track_visibility='onchange',)

    number_of_communications = fields.Integer(
        string='Number of communications',
        compute='_compute_number_of_communications',)

    is_rejected = fields.Boolean(
        string='Rejected complaint',
        default=False,
        readonly=True,
        track_visibility='onchange',)

    rejection_cause = fields.Text(
        string='Cause of the rejection',)

    is_extended = fields.Boolean(
        string='Extended process',
        default=False,
        readonly=True,
        track_visibility='onchange',)

    param_notice_period = fields.Integer(
        string='Notice Period (number of days)',
        compute='_compute_param_notice_period',)

    param_deadline = fields.Integer(
        string='Deadline (number of months)',
        compute='_compute_param_deadline',)

    param_deadline_extended = fields.Integer(
        string='Extended Deadline (number of months)',
        compute='_compute_param_deadline_extended',)

    deadline_date = fields.Date(
        string='Deadline Date',
        compute='_compute_deadline_date',)

    deadline_state = fields.Selection(
        string='Deadline Status',
        selection=[
            ('01_on_time',
             'Instruction on time'),
            ('02_upcoming_expiration',
             'Instruction deadline soon to expire'),
            ('03_expirated',
             'Instruction period expirated'),
            ('04_extended',
             'Extended instruction on time'),
            ('05_extended_upcoming_expiration',
             'Extended instruction deadline soon to expire'),
            ('06_extended_expirated',
             'Extended instruction period expirated'),
            ('07_finished',
             'Instruction finished'),
            ('99_rejected',
             'Instruction rejected'),
        ],
        default='01_on_time',
        compute='_compute_deadline_state',)

    infringement_level = fields.Selection(
        string="Infringement Level",
        selection=[
            ('01_mild',
             'Mild'),
            ('02_serious',
             'Serious'),
            ('03_very_serious',
             'Very Serious'),
        ],
        default='01_mild',
        required=True,
        index=True,)

    is_juditial_action = fields.Boolean(
        string='Juditial Action',
        default=False,)

    setted_sequence = fields.Boolean(
        string='Setted Sequence (y/n)',
        default=_default_setted_sequence,
        compute='_compute_setted_sequence',)

    decrypted_tracking_code = fields.Char(
        string='Decrypted tracking code',
        compute='_compute_decrypted_tracking_code',)

    decrypted_complainant_name = fields.Char(
        string='Decrypted complainant name',
        compute='_compute_decrypted_complainant_name',)

    decrypted_complainant_email = fields.Char(
        string='Decrypted complainant e-mail',
        compute='_compute_decrypted_complainant_email',)

    decrypted_complainant_phone = fields.Char(
        string='Decrypted complainant phone',
        compute='_compute_decrypted_complainant_phone',)

    decrypted_witness_name = fields.Char(
        string='Decrypted witness name',
        compute='_compute_decrypted_witness_name',)

    @api.depends('complaint_time')
    def _compute_complaint_date(self):
        for record in self:
            complaint_date = None
            if record.complaint_time:
                complaint_date = record.complaint_time
            record.complaint_date = complaint_date

    @api.multi
    def _compute_is_anonymous(self):
        for record in self:
            is_anonymous = True
            if (record.complainant_name or record.complainant_vat or
               record.complainant_phone):
                is_anonymous = False
            record.is_anonymous = is_anonymous

    @api.multi
    def _compute_user_in_group_cim_settings(self):
        user_in_group_cim_settings = \
            self.env.user.has_group(
                'cim_complaints_channel.group_cim_settings')
        for record in self:
            record.user_in_group_cim_settings = user_in_group_cim_settings

    @api.depends('state')
    def _compute_investigating_user_id(self):
        for record in self:
            investigating_user_id = None
            if record.state and record.state == '03_in_progress':
                investigating_user_id = self.env.user.id
            record.investigating_user_id = investigating_user_id

    @api.multi
    def _compute_number_of_communications(self):
        for record in self:
            number_of_communications = 0
            # Provisional
            number_of_communications = 10
            # TODO...
            record.number_of_communications = number_of_communications

    @api.multi
    def _compute_param_notice_period(self):
        param_notice_period = self.env['ir.values'].get_default(
            'res.cim.config.settings', 'notice_period')
        if not param_notice_period:
            param_notice_period = 10
        for record in self:
            record.param_notice_period = param_notice_period

    @api.multi
    def _compute_param_deadline(self):
        param_deadline = self.env['ir.values'].get_default(
            'res.cim.config.settings', 'deadline')
        if not param_deadline:
            param_deadline = 1
        for record in self:
            record.param_deadline = param_deadline

    @api.multi
    def _compute_param_deadline_extended(self):
        param_deadline_extended = self.env['ir.values'].get_default(
            'res.cim.config.settings', 'deadline_extended')
        if not param_deadline_extended:
            param_deadline_extended = 1
        for record in self:
            record.param_deadline_extended = param_deadline_extended

    @api.multi
    def _compute_deadline_date(self):
        for record in self:
            instruction_months = record.param_deadline
            if record.is_extended:
                instruction_months = record.param_deadline_extended
            deadline_date = (datetime.strptime(
                record.creation_date, '%Y-%m-%d') +
                relativedelta(months=instruction_months) +
                relativedelta(days=-1)).strftime('%Y-%m-%d')
            record.deadline_date = deadline_date

    @api.multi
    def _compute_deadline_state(self):
        for record in self:
            deadline_state = '99_rejected'
            if not record.is_rejected:
                deadline_state = '01_on_time'
                current_date = datetime.today().strftime('%Y-%m-%d')
                # Provisional (test: add days to current_date)
                current_date = (datetime.strptime(
                    current_date, '%Y-%m-%d') + relativedelta(
                    days=73)).strftime('%Y-%m-%d')
                # Provisional (end of test)
                deadline_date_normal = \
                    ((datetime.strptime(record.creation_date, '%Y-%m-%d') +
                      relativedelta(months=record.param_deadline) +
                      relativedelta(days=-1)).strftime('%Y-%m-%d'))
                if current_date <= deadline_date_normal:
                    deadline_notice_normal = (datetime.strptime(
                        deadline_date_normal, '%Y-%m-%d') + relativedelta(
                        days=-record.param_notice_period)).strftime('%Y-%m-%d')
                    if current_date >= deadline_notice_normal:
                        deadline_state = '02_upcoming_expiration'
                else:
                    if record.is_extended:
                        # Provisional (TODO)
                        print 'extended...'
                    else:
                        deadline_state = '03_expirated'
            record.deadline_state = deadline_state

    def _compute_setted_sequence(self):
        sequence_complaint_code_id = self.env['ir.values'].get_default(
            'res.cim.config.settings', 'sequence_complaint_code_id')
        for record in self:
            setted_sequence = False
            if sequence_complaint_code_id:
                setted_sequence = True
            record.setted_sequence = setted_sequence

    @api.multi
    def _compute_decrypted_tracking_code(self):
        for record in self:
            decrypted_tracking_code = ''
            if record.tracking_code:
                # Provisional
                decrypted_tracking_code = record.tracking_code
                # TODO
            record.decrypted_tracking_code = decrypted_tracking_code

    @api.multi
    def _compute_decrypted_complainant_name(self):
        for record in self:
            decrypted_complainant_name = ''
            if record.decrypted_complainant_name:
                # Provisional
                # TODO...
                decrypted_complainant_name = \
                    record.decrypted_complainant_name
            record.decrypted_complainant_name = \
                decrypted_complainant_name

    @api.multi
    def _compute_decrypted_complainant_email(self):
        for record in self:
            decrypted_complainant_email = ''
            if record.decrypted_complainant_email:
                # Provisional
                # TODO...
                decrypted_complainant_email = \
                    record.decrypted_complainant_email
            record.decrypted_complainant_email = \
                decrypted_complainant_email

    @api.multi
    def _compute_decrypted_complainant_vat(self):
        for record in self:
            decrypted_complainant_vat = ''
            if record.decrypted_complainant_vat:
                # Provisional
                # TODO...
                decrypted_complainant_vat = \
                    record.decrypted_complainant_vat
            record.decrypted_complainant_vat = \
                decrypted_complainant_vat

    @api.multi
    def _compute_decrypted_complainant_phone(self):
        for record in self:
            decrypted_complainant_phone = ''
            if record.decrypted_complainant_phone:
                # Provisional
                # TODO...
                decrypted_complainant_phone = \
                    record.decrypted_complainant_phone
            record.decrypted_complainant_phone = \
                decrypted_complainant_phone

    @api.multi
    def _compute_decrypted_witness_name(self):
        for record in self:
            decrypted_witness_name = ''
            if record.decrypted_witness_name:
                # Provisional
                # TODO...
                decrypted_witness_name = \
                    record.decrypted_witness_name
            record.decrypted_witness_name = \
                decrypted_witness_name

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            display_name = record.name + \
                ' (' + record.complaint_type_id.name + ')'
            result.append((record.id, display_name))
        return result

    @api.model
    def create(self, vals):
        sequence_complaint_code_id = self.env['ir.values'].get_default(
            'res.cim.config.settings', 'sequence_complaint_code_id')
        if sequence_complaint_code_id:
            model_ir_sequence = self.env['ir.sequence'].sudo()
            sequence_complaint_code = \
                model_ir_sequence.browse(sequence_complaint_code_id)
            if sequence_complaint_code:
                new_code = model_ir_sequence.next_by_code(
                    sequence_complaint_code.code)
                vals['name'] = new_code
        else:
            if 'name' in vals and vals['name']:
                vals['name'] = vals['name'].strip()
        if ('name' not in vals) or (not vals['name']):
            raise exceptions.ValidationError(_('It is mandatory to enter a '
                                               'code for the new complaint.'))
        new_complaint = super(CimComplaint, self).create(vals)
        return new_complaint

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(CimComplaint, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if (not self.env.user.has_group(
                'cim_complaints_channel.group_cim_settings')):
            if view_type == 'tree':
                doc = etree.XML(res['arch'])
                nodes = doc.xpath('//tree')
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)
            if view_type == 'form':
                doc = etree.XML(res['arch'])
                nodes = doc.xpath('//form')
                for node in nodes:
                    node.set('create', '0')
                res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def action_get_communications(self):
        self.ensure_one()
        # Provisional
        print 'action_get_communications...'
        # TODO...

    @api.multi
    def action_go_to_state_02_admitted(self):
        self.ensure_one()
        # Provisional
        print 'action_go_to_state_02_admitted...'
        # TODO...

    @api.multi
    def action_reject(self):
        self.ensure_one()
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Complaint') + ' : ' + self.name,
            'res_model': 'wizard.reject.complaint',
            'src_model': 'cim.complaint',
            'view_mode': 'form',
            'target': 'new',
            }
        return act_window
