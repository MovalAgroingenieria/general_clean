# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _
import datetime


class ResFile(models.Model):
    """A register class to log all movements regarding files"""
    _name = 'res.file'
    _description = "Log of Files Movements"
    _inherit = 'mail.thread'

    SIZE_ANNUALSEQ_CODE = 4

    def _default_file_code(self):
        current_year = datetime.datetime.now().year
        prefix = ''
        default_annual_seq_prefix = self.env['ir.values'].get_default(
            'res.file.config.settings', 'default_annual_seq_prefix')
        if default_annual_seq_prefix:
            default_annual_seq_prefix = default_annual_seq_prefix.strip()
            if default_annual_seq_prefix != '':
                prefix = default_annual_seq_prefix
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

    name = fields.Char(
        string='Code',
        size=30,
        default=_default_file_code,
        required=True,
        index=True)

    date_file = fields.Date(
        string='Discharge date',
        default=lambda self: fields.datetime.now(),
        required=True,
        index=True)

    subject = fields.Char(
        string='Subject',
        size=150,
        required=True,
        index=True)

    tag_ids = fields.Many2many(
        string='File Tags',
        comodel_name='res.filetag',
        relation='res_file_filetag_rel',
        column1='file_id', column2='filetag_id')

    image = fields.Binary(
        string='Photo / Image',
        attachment=True)

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
        track_visibility='onchange')

    is_blocked = fields.Boolean(
        string='Blocked',
        default=False,
        track_visibility='onchange')

    is_cancelled = fields.Boolean(
        string='Cancelled',
        default=False,
        track_visibility='onchange')

    notes = fields.Html(
        string='Notes')

    category_id = fields.Many2one(
        string='Category',
        comodel_name='res.file.category',
        index=True,
        required=True,
        ondelete='restrict',
        default=_default_category_id)

    partnerlink_ids = fields.One2many(
        string='Partners',
        comodel_name='res.file.partnerlink',
        inverse_name='file_id')

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        index=True,
        ondelete='restrict',
        store=True,
        compute='_compute_partner_id',
        track_visibility='onchange')

    filelink_ids = fields.One2many(
        string='Files',
        comodel_name='res.file.filelink',
        inverse_name='file_id')

    file_res_letter_ids = fields.One2many(
        string='File registry',
        comodel_name='res.letter',
        inverse_name='file_id')

    number_of_file_registers = fields.Integer(
        string='Num. file registers',
        compute='_compute_number_of_file_registers')

    color = fields.Integer(
        string='Color Index',
        default="0",
        help='0:grey, 1:green, 2:yellow, 3:orange, 4:red, 5:purple, 6:blue, '
             '7:cyan, 8:light-green, 9:magenta')

    closing_date = fields.Date(
        string='Closing date',
        store=True,
        compute="_compute_closing_date")

    container_id = fields.Many2one(
        string='Container',
        comodel_name='res.file.container')

    file_attachment_ids = fields.One2many(
        string="File attachments",
        comodel_name="ir.attachment",
        compute="_compute_attachments_ids")

    has_filelinks = fields.Boolean(
        string='Has filelinks',
        default=False,
        compute="_compute_has_filelinks")

    has_attachments = fields.Boolean(
        string='Has attachments',
        default=False,
        compute="_compute_has_attachments")

    has_registres = fields.Boolean(
        string='Has registres',
        default=False,
        compute="_compute_has_registres")

    _sql_constraints = [
        ('unique_name',
         'UNIQUE (name)',
         'Existing file code.'),
        ]

    @api.multi
    def action_validate_file(self):
        self.ensure_one()
        self.state = '02_inprogress'

    @api.multi
    def action_close_file(self):
        self.ensure_one()
        if self.is_blocked:
            self.state = False
        else:
            self.state = '03_closed'

    @api.multi
    def action_block_file(self):
        self.ensure_one()
        self.is_blocked = True

    @api.multi
    def action_unblock_file(self):
        self.ensure_one()
        self.is_blocked = False

    @api.multi
    def action_cancel_file(self):
        self.ensure_one()
        self.is_cancelled = True

    @api.multi
    def action_reactive_file(self):
        self.ensure_one()
        self.is_cancelled = False

    @api.multi
    def action_reactive_file_to_draft(self):
        self.ensure_one()
        self.state = '01_draft'

    @api.multi
    def action_reactive_file_to_inprogress(self):
        self.ensure_one()
        self.state = '02_inprogress'

    @api.multi
    def action_get_file_registers(self):
        self.ensure_one()
        if self.file_res_letter_ids:
            id_tree_view = self.env.ref('crm_lettermgmt.'
                                        'res_letter_tree_o2m_view').id
            id_form_view = self.env.ref('crm_lettermgmt.'
                                        'res_letter_form_view').id
            search_view = self.env.ref('crm_lettermgmt.res_letter_filter')
            act_window = {
                'type': 'ir.actions.act_window',
                'name': _('File registers'),
                'res_model': 'res.letter',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(id_tree_view, 'tree'),
                          (id_form_view, 'form')],
                'search_view_id': (search_view.id, search_view.name),
                'target': 'current',
                'domain': [('id', 'in', self.file_res_letter_ids.ids)],
                }
            return act_window

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.subject:
                name = record.name + ' ' + '[' + record.subject + ']'
            else:
                name = record.name + ' ' + _('[no subject]')
            result.append((record.id, name))
        return result

    @api.multi
    def _compute_attachments_ids(self):
        for record in self:
            record.file_attachment_ids = record.env['ir.attachment'].search(
                [('res_model', '=', record._name), ('res_id', '=', record.id)])

    @api.depends('partnerlink_ids')
    def _compute_partner_id(self):
        for record in self:
            partner_id = None
            for partnerlink in record.partnerlink_ids:
                if partnerlink.is_main:
                    partner_id = partnerlink.partner_id
                    break
            record.partner_id = partner_id

    @api.depends('file_res_letter_ids')
    def _compute_number_of_file_registers(self):
        for record in self:
            number_of_file_registers = 0
            file_registers = self.env['res.letter'].search(
                [('file_id', '=', record.id)])
            if file_registers:
                number_of_file_registers = len(file_registers)
            record.number_of_file_registers = number_of_file_registers

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

    @api.depends('file_res_letter_ids')
    def _compute_has_registres(self):
        for record in self:
            has_registres = False
            if record.file_res_letter_ids:
                has_registres = True
            record.has_registres = has_registres

    @api.model
    def create(self, vals):
        if 'name' in vals:
            current_file_name = vals['name']
            default_annual_seq_prefix = self.env['ir.values'].get_default(
                'res.file.config.settings', 'default_annual_seq_prefix')
            if default_annual_seq_prefix:
                after_prefix = \
                    current_file_name[len(default_annual_seq_prefix):]
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
                    file_number = int(current_file_name.split('/')[1])
                except Exception:
                    raise exceptions.UserError(
                        _('The file number must be an integer.'))
        new_file = super(ResFile, self).create(vals)
        return new_file

    @api.constrains('partnerlink_ids')
    def _check_partnerlink_ids(self):
        if len(self) == 1:
            file = self
            if file.partnerlink_ids:
                main_partnerlinks = filter(lambda x: x['is_main'] is True,
                                           file.partnerlink_ids)
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

    @api.model_cr
    def init(self):
        enable_read_permission = self.env['ir.values'].get_default(
            'res.file.config.settings',
            'enable_access_file_filemgmt_portal_user')
        config_model = self.env['res.file.config.settings']
        config_model.sudo().assign_permissions_on_resfile_to_portaluser(
            enable_read_permission)


class ResFilePartnerlink(models.Model):
    _name = 'res.file.partnerlink'

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
