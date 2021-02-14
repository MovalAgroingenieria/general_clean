# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _
import datetime


class ResFile(models.Model):
    """A register class to log all movements regarding files"""
    _name = 'res.file'
    _description = "Log of Files Movements"
    _inherit = ['mail.thread', 'simple.model']

    _size_name = 50
    _size_description = 100
    _set_num_code = False

    SIZE_ANNUALSEQ_CODE = 4

    def _default_alphanum_code(self):
        current_year = datetime.datetime.now().year
        prefix = ''
        annual_seq_prefix = self.env['ir.config_parameter'].sudo().get_param(
            'crm_filemgmt.annual_seq_prefix')
        if annual_seq_prefix:
            annual_seq_prefix = annual_seq_prefix.strip()
            if annual_seq_prefix != '':
                prefix = annual_seq_prefix
        else:
            raise exceptions.UserError(
                _('The prefix for the file names has not been set.'))
        if prefix != '':
            prefix = prefix + '-'
        full_prefix = prefix + str(current_year).zfill(4) + '/'
        resp = full_prefix + '1'.zfill(self.SIZE_ANNUALSEQ_CODE)
        files = self.search([('name', 'like', full_prefix)],
                            limit=1, order='name desc')
        if len(files) == 1:
            last_code = files[0].name
            if len(last_code) > len(full_prefix):
                numeric_suffix = \
                    last_code[-(len(last_code) - len(full_prefix)):]
                try:
                    proposed_code = int(numeric_suffix)
                except Exception:
                    proposed_code = 0
                if proposed_code > 0:
                    resp = full_prefix + \
                        str(proposed_code + 1).zfill(
                            self.SIZE_ANNUALSEQ_CODE)
        return resp

    def _default_category_id(self):
        resp = 0
        proposed_category = self.env.ref(
            'crm_filemgmt.resfilecategory_internal_file')
        if proposed_category:
            resp = proposed_category.id
        return resp

    alphanum_code = fields.Char(
        string='Code',
        default=_default_alphanum_code,
        required=True,)

    date_file = fields.Date(
        string='Discharge date',
        default=lambda self: fields.datetime.now(),
        required=True,
        index=True,)

    subject = fields.Char(
        string='Subject',
        size=150,
        required=True,
        index=True,)

    tag_ids = fields.Many2many(
        string='File Tags',
        comodel_name='res.filetag',
        relation='res_file_filetag_rel',
        column1='file_id', column2='filetag_id',)

    image = fields.Image(
        string='Photo / Image',)

    state = fields.Selection(
        selection=[
            ('01_draft', 'Draft'),
            ('02_inprogress', 'In progress'),
            ('03_closed', 'Closed'),
        ],
        string='State',
        default='01_draft',
        required=True,
        index=True,
        tracking=True,)

    is_blocked = fields.Boolean(
        string='Blocked',
        default=False,
        tracking=True,)

    is_cancelled = fields.Boolean(
        string='Cancelled',
        default=False,
        tracking=True,)

    category_id = fields.Many2one(
        string='Category',
        comodel_name='res.file.category',
        index=True,
        required=True,
        ondelete='restrict',
        default=_default_category_id,)

    partnerlink_ids = fields.One2many(
        string='Partners',
        comodel_name='res.file.partnerlink',
        inverse_name='file_id',)

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        index=True,
        ondelete='restrict',
        store=True,
        compute='_compute_partner_id',
        tracking=True,)

    filelink_ids = fields.One2many(
        string='Files',
        comodel_name='res.file.filelink',
        inverse_name='file_id',)

    color = fields.Integer(
        string='Color Index',
        default="0",
        help='0:no-color, 1:red, 2:orange, 3:yellow, 4:Cyan, 5:dark-purple, '
             '6:pink, 7:blue, 8:dark-blue, 9:magenta, 10:green, 11:purple',)

    closing_date = fields.Date(
        string='Closing date',
        store=True,
        compute="_compute_closing_date",)

    container_id = fields.Many2one(
        string='Container',
        comodel_name='res.file.container',)

    file_attachment_ids = fields.One2many(
        string="File attachments",
        comodel_name="ir.attachment",
        compute="_compute_attachments_ids",)

    has_filelinks = fields.Boolean(
        string='Has filelinks',
        default=False,
        compute="_compute_has_filelinks",)

    has_attachments = fields.Boolean(
        string='Has attachments',
        default=False,
        compute="_compute_has_attachments",)

    @api.depends('partnerlink_ids')
    def _compute_partner_id(self):
        for record in self:
            partner_id = None
            for partnerlink in record.partnerlink_ids:
                if partnerlink.is_main:
                    partner_id = partnerlink.partner_id
                    break
            record.partner_id = partner_id

    @api.depends('state')
    def _compute_closing_date(self):
        for record in self:
            if record.state == '03_closed':
                record.closing_date = datetime.datetime.now()
            else:
                record.closing_date = False

    @api.depends('filelink_ids')
    def _compute_has_filelinks(self):
        for record in self:
            has_filelinks = False
            if record.filelink_ids:
                has_filelinks = True
            record.has_filelinks = has_filelinks

    @api.depends('file_attachment_ids')
    def _compute_has_attachments(self):
        for record in self:
            has_attachments = False
            if record.file_attachment_ids:
                has_attachments = True
            record.has_attachments = has_attachments

    def action_validate_file(self):
        self.ensure_one()
        self.state = '02_inprogress'

    def action_close_file(self):
        self.ensure_one()
        if self.is_blocked:
            self.state = False
        else:
            self.state = '03_closed'

    def action_block_file(self):
        self.ensure_one()
        self.is_blocked = True

    def action_unblock_file(self):
        self.ensure_one()
        self.is_blocked = False

    def action_cancel_file(self):
        self.ensure_one()
        self.is_cancelled = True

    def action_reactive_file(self):
        self.ensure_one()
        self.is_cancelled = False

    def action_reactive_file_to_draft(self):
        self.ensure_one()
        self.state = '01_draft'

    def action_reactive_file_to_inprogress(self):
        self.ensure_one()
        self.state = '02_inprogress'

    def name_get(self):
        result = []
        for record in self:
            if record.subject:
                name = record.alphanum_code + ' ' + '[' + record.subject + ']'
            else:
                name = record.alphanum_code + ' ' + _('[no subject]')
            result.append((record.id, name))
        return result

    def _compute_attachments_ids(self):
        for record in self:
            record.file_attachment_ids = record.env['ir.attachment'].search(
                [('res_model', '=', record._name), ('res_id', '=', record.id)])

    def _process_vals(self, vals):
        vals = super(ResFile, self)._process_vals(vals)
        if 'alphanum_code' in vals:
            current_file_name = vals['alphanum_code']
            annual_seq_prefix = \
                self.env['ir.config_parameter'].sudo().get_param(
                    'crm_filemgmt.annual_seq_prefix')
            if annual_seq_prefix:
                after_prefix = \
                    current_file_name[len(annual_seq_prefix):]
                if not after_prefix.startswith('-'):
                    raise exceptions.UserError(
                        _('The prefix must be separated from the rest of the '
                          'file name by a hyphen (-).'))
            if '/' in current_file_name:
                if current_file_name.startswith('/') or \
                        current_file_name.endswith('/'):
                    raise exceptions.UserError(
                        _('The file name cannot start or end with a '
                          'slash (/).'))
                count = 0
                for i in current_file_name:
                    if i == '/':
                        count += 1
                if count > 1:
                    raise exceptions.UserError(
                        _('There cannot be more than one slash in the name of '
                          'the file.'))
                try:
                    file_number = int(current_file_name.split('/')[1].strip())
                except Exception:
                    raise exceptions.UserError(
                        _('The file number must have an integer the same '
                          'length as the size of the annual sequence '
                          '%s digits.') % self.SIZE_ANNUALSEQ_CODE)
        return vals

    @api.constrains('partnerlink_ids')
    def _check_partnerlink_ids(self):
        if len(self) == 1:
            file = self
            if file.partnerlink_ids:
                main_partnerlinks = filter(lambda x: x['is_main'] is True,
                                           file.partnerlink_ids)
                main_partnerlinks = list(main_partnerlinks)
                if main_partnerlinks:
                    if len(main_partnerlinks) == 0:
                        raise exceptions.UserError(
                            _('It is mandatory to check the primary partner.'))
                    if len(main_partnerlinks) > 1:
                        raise exceptions.UserError(
                            _('Only one primary partner is allowed.'))
            unique_ids_of_partner = []
            for partnerlink in file.partnerlink_ids:
                unique_ids_of_partner.append(partnerlink.partner_id.id)
            unique_ids_of_partner = list(set(unique_ids_of_partner))
            if len(unique_ids_of_partner) != len(file.partnerlink_ids):
                raise exceptions.UserError(_('There are repeated partners.'))

    @api.constrains('filelink_ids')
    def _check_filelink_ids(self):
        if len(self) == 1:
            file = self
            if file.filelink_ids:
                self_referenced_file = self.env['res.file.filelink'].search(
                    [('file_id', '=', file.id),
                     (('related_file_id', '=', file.id))])
                if self_referenced_file:
                    raise exceptions.UserError(_('The file cannot be '
                                                 'self-referenced.'))
            unique_ids_of_file = []
            for filelink in file.filelink_ids:
                unique_ids_of_file.append(filelink.related_file_id.id)
            unique_ids_of_file = list(set(unique_ids_of_file))
            if len(unique_ids_of_file) != len(file.filelink_ids):
                raise exceptions.UserError(_('There are repeated files.'))


class ResFilePartnerlink(models.Model):
    _name = 'res.file.partnerlink'
    _description = 'File partnerlinks'

    file_id = fields.Many2one(
        string='File',
        comodel_name='res.file',
        required=True,
        index=True,
        ondelete='cascade')

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        required=True,
        index=True,
        ondelete='restrict')

    is_main = fields.Boolean(
        string='Primary',
        default=True,
        help='If checked, this partner will be the primary')

    subject = fields.Char(
        string='Subject',
        related='file_id.subject')

    date_file = fields.Date(
        string='Discharge date',
        related='file_id.date_file')

    state = fields.Selection(
        string='State',
        related='file_id.state')


class ResFileFilelink(models.Model):
    _name = 'res.file.filelink'
    _description = 'File filelinks'

    file_id = fields.Many2one(
        string='File',
        comodel_name='res.file',
        required=True,
        index=True,
        ondelete='cascade')

    related_file_id = fields.Many2one(
        string='Related File',
        comodel_name='res.file',
        required=True,
        ondelete='restrict')

    related_file_subject = fields.Char(
        string='Subject',
        related='related_file_id.subject')
