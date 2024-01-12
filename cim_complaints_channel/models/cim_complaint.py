# -*- coding: utf-8 -*-
# Copyright 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class CimComplaint(models.Model):
    _name = 'cim.complaint'
    _description = 'Complaint'
    _order = 'name'

    SIZE_SMALL = 25
    SIZE_MEDIUM = 50
    SIZE_MEDIUM_EXTRA = 75
    SIZE_NORMAL = 100

    name = fields.Char(
        string='Code',
        size=SIZE_SMALL,
        required=True,
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
        string="State",
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

    deadline_date = fields.Date(
        string='Deadline Date',)

    complainant_email = fields.Char(
        string='Complainant E-mail',
        size=SIZE_MEDIUM,
        index=True,)

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
        index=True,)

    investigating_user_id = fields.Many2one(
        string='Instructor',
        comodel_name='res.users',
        store=True,
        compute='_compute_investigating_user_id')

    number_of_communications = fields.Integer(
        string='Number of communications',
        compute='_compute_number_of_communications',)

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
    def _compute_deadline_state(self):
        for record in self:
            deadline_state = '01_on_time'
            # PROVISIONAL
            # TODO...
            record.deadline_state = deadline_state

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
    def action_get_communications(self):
        self.ensure_one()
        # Provisional
        print 'action_get_communications...'
        # TODO...

    @api.multi
    def action_go_to_state_04_ready(self):
        self.ensure_one()
        # Provisional
        print 'action_go_to_state_04_ready...'
        # TODO...

    @api.multi
    def action_go_to_state_previous(self):
        self.ensure_one()
        # Provisional
        print 'action_go_to_state_previous...'
        # TODO...
