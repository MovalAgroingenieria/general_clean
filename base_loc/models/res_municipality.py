# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, exceptions, _


class ResMunicipality(models.Model):
    _name = 'res.municipality'
    _description = 'Municipality'
    _inherit = 'simple.model'
    _order = 'cadastral_code'

    # Size of "cadastral_code" field, in the model.
    MAX_SIZE_CADASTRAL_CODE = 20

    _size_name = 50
    _set_num_code = False
    _set_alphanum_code_to_lowercase = False
    _set_alphanum_code_to_uppercase = False
    _size_suffix_cadastral_code = 3

    def _default_province_id(self):
        resp = 0
        current_province_id = \
            self.env.context.get('current_province_id', False)
        if current_province_id:
            resp = current_province_id
        else:
            resp = self._get_province()
        return resp

    alphanum_code = fields.Char(
        string='Municipality',
        required=True,
        translate=True,)

    province_id = fields.Many2one(
        string='Province',
        comodel_name='res.province',
        default=_default_province_id,
        required=True,
        index=True,
        ondelete='restrict',)

    region_id = fields.Many2one(
        string='Region',
        comodel_name='res.region',
        store=True,
        index=True,
        compute='_compute_region_id',)

    suffix_cadastral_code = fields.Integer(
        string='Cadastral Code (suffix)',
        default=1,
        required=True,)

    cadastral_code = fields.Char(
        string='Cadastral Code',
        size=MAX_SIZE_CADASTRAL_CODE,
        store=True,
        index=True,
        compute='_compute_cadastral_code',)

    place_ids = fields.One2many(
        string='Places',
        comodel_name='res.place',
        inverse_name='municipality_id',)

    number_of_places = fields.Integer(
        string='Number of places',
        compute='_compute_number_of_places',)

    _sql_constraints = [
        ('cadastral_code_unique',
         'UNIQUE (cadastral_code)',
         'Existing Code.'),
        ('cadastral_code_positive',
         'CHECK (suffix_cadastral_code > 0)',
         'A valid code is required.'),
        ]

    @api.depends('province_id', 'province_id.region_id')
    def _compute_region_id(self):
        for record in self:
            region_id = None
            if record.province_id:
                region_id = record.province_id.region_id
            record.region_id = region_id

    @api.depends('province_id', 'province_id.cadastral_code',
                 'suffix_cadastral_code')
    def _compute_cadastral_code(self):
        for record in self:
            cadastral_code = ''
            if (record.province_id and record.province_id.cadastral_code and
               record.suffix_cadastral_code):
                cadastral_code = record.province_id.cadastral_code + \
                    str(record.suffix_cadastral_code).zfill(
                        self._size_suffix_cadastral_code)
            record.cadastral_code = cadastral_code

    def _compute_number_of_places(self):
        for record in self:
            number_of_places = 0
            if record.place_ids:
                number_of_places = len(record.place_ids)
            record.number_of_places = number_of_places

    @api.constrains('suffix_cadastral_code')
    def _check_suffix_cadastral_code(self):
        max_cadastral_code = (10 ** self._size_suffix_cadastral_code) - 1
        for record in self:
            if record.suffix_cadastral_code > max_cadastral_code:
                raise exceptions.ValidationError(_('Code too big.'))

    def name_get(self):
        resp = []
        add_province = \
            self.env.context.get('municipality_with_province', False)
        for record in self:
            name = record.alphanum_code
            if add_province:
                name = name + ' (' + record.province_id.alphanum_code + ')'
            resp.append((record.id, name))
        return resp

    def action_show_places(self):
        self.ensure_one()
        current_municipality = self
        id_tree_view = self.env.ref(
            'base_loc.res_place_view_tree').id
        id_form_view = self.env.ref(
            'base_loc.res_place_view_form').id
        search_view = self.env.ref(
            'base_loc.res_place_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Places'),
            'res_model': 'res.place',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree'), (id_form_view, 'form')],
            'search_view_id': (search_view.id, search_view.name),
            'target': 'current',
            'domain': [('municipality_id', '=', current_municipality.id)],
            'context': {'current_municipality_id': current_municipality.id, }
            }
        return act_window

    def _get_province(self):
        resp = 0
        provinces = self.env['res.province'].search([])
        if provinces and len(provinces) == 1:
            resp = provinces[0].id
        return resp
