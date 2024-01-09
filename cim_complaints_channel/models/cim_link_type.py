# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


class CimLinkType(models.Model):
    _name = 'cim.link.type'
    _description = 'Link Type'
    _order = 'name'

    SIZE_NAME = 75

    name = fields.Char(
        string='Name',
        size=SIZE_NAME,
        required=True,
        index=True,
        translate=True,)

    is_standard = fields.Boolean(
        string='Standard Type (y/n)',
        default=False)

    number_of_complaints = fields.Integer(
        string='Number of complaints',
        compute='_compute_number_of_complaints',)

    notes = fields.Html(
        string='Notes',)

    notes_text = fields.Char(
        string='Notes (as text)',
        compute='_compute_notes_text',)

    @api.multi
    def _compute_number_of_complaints(self):
        for record in self:
            number_of_complaints = 0
            # Provisional
            # TODO...
            record.number_of_complaints = number_of_complaints

    @api.multi
    def _compute_notes_text(self):
        model_converter = self.env['ir.fields.converter']
        for record in self:
            notes_text = ''
            if record.notes:
                notes_text = model_converter.text_from_html(
                    record.notes, 50, 150)
            record.notes_text = notes_text

    @api.multi
    def unlink(self):
        for record in self:
            if record.is_standard:
                raise exceptions.UserError(_('It is not possible to remove '
                                             'a \'STANDARD\' link type.'))
        res = super(CimLinkType, self).unlink()
        return res
