# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class SimpleModel(models.AbstractModel):
    _name = 'simple.model'
    _description = 'Simple Model'
    _order = 'name'

    # Size of "name" and "alphanum_code" field, in the model.
    MAX_SIZE_NAME_FIELD = 50

    # Size of fields of char type, in the model.
    MAX_SIZE_CHAR_FIELD = 255

    # Size of "name" and "alphanum_code" fields, in the form view.
    _size_name = 30

    # Size of "description" field, in the form view.
    _size_description = 75

    # Are the codes numeric values?
    _set_num_code = False

    # If the code is an alphanumeric value, convert it to lowercase?
    _set_alphanum_code_to_lowercase = False

    # If the code is an alphanumeric value, convert it to uppercase?
    _set_alphanum_code_to_uppercase = False

    def _default_num_code(self):
        resp = 0
        if self._set_num_code:
            records = self.search([], limit=1,
                                  order='num_code desc')
            if records:
                resp = records[0].num_code + 1
            else:
                resp = 1
            return resp
        return resp

    alphanum_code = fields.Char(
        string='Code (alphanumeric value)',
        size=MAX_SIZE_NAME_FIELD,
        index=True,)

    num_code = fields.Integer(
        string='Code (numeric value)',
        default=_default_num_code,
        index=True,)

    description = fields.Char(
        string='Description',
        size=MAX_SIZE_CHAR_FIELD,
        index=True,)

    name = fields.Char(
        string='Code (name)',
        size=MAX_SIZE_NAME_FIELD,
        store=True,
        index=True,
        compute='_compute_name',)

    notes = fields.Html(
        string='Notes',)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE (name)',
         'Existing Code.'),
        ('name_not_null',
         'CHECK (alphanum_code IS NOT NULL OR num_code > 0)',
         'A valid code is required.'),
        ('description_not_null',
         'CHECK (description IS NOT NULL OR alphanum_code IS NOT NULL)',
         'The description is required.'),
        ]

    @api.depends('alphanum_code', 'num_code')
    def _compute_name(self):
        for record in self:
            name = record.alphanum_code
            if self._set_num_code:
                name = '0'.zfill(self._size_name)
                if record.num_code:
                    name = str(record.num_code).zfill(self._size_name)
            record.name = name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if self._set_num_code:
            records = self.search(
                [('description', 'ilike', name)] + args, limit=limit)
        else:
            records = self.search(
                [('alphanum_code', 'ilike', name)] + args, limit=limit)
        return records.name_get()

    def name_get(self):
        resp = []
        for record in self:
            name = record.alphanum_code
            if self._set_num_code:
                description = ''
                if record.description:
                    description = record.description
                name = description + ' [' + str(record.num_code) + ']'
            resp.append((record.id, name))
        return resp

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'alphanum_code' in vals and vals['alphanum_code']:
                original_alphanum_code = vals['alphanum_code']
                final_alphanum_code = self._process_alphanum_code(
                    original_alphanum_code)
                vals['alphanum_code'] = final_alphanum_code
            if 'description' in vals and vals['description']:
                original_description = vals['description']
                final_description = self._process_description(
                    original_description)
                vals['description'] = final_description
            vals = self._process_vals(vals)
        records = super(SimpleModel, self).create(vals_list)
        return records

    def write(self, vals):
        if 'alphanum_code' in vals and vals['alphanum_code']:
            original_alphanum_code = vals['alphanum_code']
            final_alphanum_code = self._process_alphanum_code(
                original_alphanum_code)
            vals['alphanum_code'] = final_alphanum_code
        if 'description' in vals and vals['description']:
            original_description = vals['description']
            final_description = self._process_description(
                original_description)
            vals['description'] = final_description
        vals = self._process_vals(vals)
        resp = super(SimpleModel, self).write(vals)
        return resp

    def _process_alphanum_code(self, value):
        resp = value
        if len(resp) > self._size_name:
            resp = resp[0:self._size_name]
        if self._set_alphanum_code_to_lowercase:
            resp = resp.lower()
        if self._set_alphanum_code_to_uppercase:
            resp = resp.upper()
        return resp

    def _process_description(self, value):
        resp = value
        if len(resp) > self._size_description:
            resp = resp[0:self._size_description]
        return resp

    # Hook: This method can be called to change some values of the
    # "vals" dictionary, before saving a register.
    def _process_vals(self, vals):
        return vals
