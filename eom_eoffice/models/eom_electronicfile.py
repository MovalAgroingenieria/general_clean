# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class EomElectronicfile(models.Model):
    _name = 'eom.electronicfile'
    _description = 'Electronic File'

    SIZE_NAME = 25

    def _default_name(self):
        resp = None
        sequence_electronicfile_code_id = self.env['ir.values'].get_default(
            'res.eom.config.settings', 'sequence_electronicfile_code_id')
        if sequence_electronicfile_code_id:
            model_ir_sequence = self.env['ir.sequence'].sudo()
            sequence_electronicfile_code = \
                model_ir_sequence.browse(sequence_electronicfile_code_id)
            if sequence_electronicfile_code:
                resp = model_ir_sequence.next_by_code(
                    sequence_electronicfile_code.code)
        return resp

    event_time = fields.Datetime(
        string='Time',
        default=lambda self: fields.datetime.now(),
        required=True,
        index=True,
        readonly=True,)

    digitalregister_id = fields.Many2one(
        string='Digital Certificate',
        comodel_name='eom.digitalregister',
        required=True,
        index=True,
        readonly=True,
        ondelete='restrict',)

    name = fields.Char(
        string='Code',
        size=SIZE_NAME,
        default=_default_name,
        required=True,
        index=True,)

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        store=True,
        index=True,
        compute='_compute_partner_id',
        ondelete='restrict',)

    type = fields.Selection(
        string="Type",
        selection=[
            ('01_generic_instance', 'Generic Instance'),
            ('02_suggestion', 'Suggestion'),
        ],
        default='01_generic_instance',
        required=True,
        index=True,)

    exposition = fields.Text(
        string='Exposition',
        index=True,)

    request = fields.Text(
        string='Request',)

    suggestion = fields.Text(
        string='Request',)

    firstname = fields.Char(
        string='First Name',
        store=True,
        compute='_compute_firstname',
        index=True,)

    lastname = fields.Char(
        string='Last Name',
        store=True,
        compute='_compute_lastname',
        index=True,)

    fullname = fields.Char(
        string='Full Name',
        store=True,
        compute='_compute_fullname',
        index=True,)

    editable_notes = fields.Boolean(
        string='Editable Notes (y/n)',
        compute='_compute_editable_notes',)

    notes = fields.Html(
        string='Notes',)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE (name)',
         'Existing electronic file (repeated code).'),
        ]

    @api.depends('digitalregister_id', 'digitalregister_id.partner_id')
    def _compute_partner_id(self):
        for record in self:
            partner_id = None
            if (record.digitalregister_id and
               record.digitalregister_id.partner_id):
                partner_id = record.digitalregister_id.partner_id
            record.partner_id = partner_id

    @api.depends('digitalregister_id', 'digitalregister_id.firstname')
    def _compute_firstname(self):
        for record in self:
            firstname = ''
            if (record.digitalregister_id and
               record.digitalregister_id.firstname):
                firstname = record.digitalregister_id.firstname
            record.firstname = firstname

    @api.depends('digitalregister_id', 'digitalregister_id.lastname')
    def _compute_lastname(self):
        for record in self:
            lastname = ''
            if (record.digitalregister_id and
               record.digitalregister_id.lastname):
                lastname = record.digitalregister_id.lastname
            record.lastname = lastname

    @api.depends('digitalregister_id',
                 'digitalregister_id.firstname', 'digitalregister_id.lastname')
    def _compute_fullname(self):
        for record in self:
            fullname = ''
            if record.digitalregister_id:
                if record.digitalregister_id.lastname:
                    fullname = record.digitalregister_id.lastname
                    if record.digitalregister_id.firstname:
                        fullname = fullname + ' ' + \
                            record.digitalregister_id.firstname
                elif record.digitalregister_id.firstname:
                    fullname = record.digitalregister_id.firstname
            record.fullname = fullname

    @api.multi
    def _compute_editable_notes(self):
        editable_notes = self.env['ir.values'].get_default(
            'res.eom.config.settings', 'editable_notes')
        for record in self:
            record.editable_notes = editable_notes
