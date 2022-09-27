# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, exceptions, _


class ResProvince(models.Model):
    _name = 'res.province'
    _description = 'Province'
    _inherit = 'simple.model'
    _order = 'cadastral_code'

    # Size of "cadastral_code" field, in the model.
    MAX_SIZE_CADASTRAL_CODE = 10

    _size_name = 50
    _set_num_code = False
    _set_alphanum_code_to_lowercase = False
    _set_alphanum_code_to_uppercase = False
    _size_cadastral_code = 2

    def _default_region_id(self):
        resp = 0
        current_region_id = self.env.context.get('current_region_id', False)
        if current_region_id:
            resp = current_region_id
        else:
            resp = self._get_region()
        return resp

    alphanum_code = fields.Char(
        string='Province',
        required=True,
        translate=True,)

    region_id = fields.Many2one(
        string='Region',
        comodel_name='res.region',
        default=_default_region_id,
        required=True,
        index=True,
        ondelete='restrict',)

    num_cadastral_code = fields.Integer(
        string='Cadastral Code (num)',
        default=1,
        required=True,)

    cadastral_code = fields.Char(
        string='Cadastral Code',
        size=MAX_SIZE_CADASTRAL_CODE,
        store=True,
        index=True,
        compute='_compute_cadastral_code',)

    municipality_ids = fields.One2many(
        string='Municipalities',
        comodel_name='res.municipality',
        inverse_name='province_id',)

    number_of_municipalities = fields.Integer(
        string='Number of municipalities',
        compute='_compute_number_of_municipalities',)

    _sql_constraints = [
        ('cadastral_code_unique',
         'UNIQUE (cadastral_code)',
         'Existing Code.'),
        ('cadastral_code_positive',
         'CHECK (num_cadastral_code > 0)',
         'A valid code is required.'),
        ]

    @api.depends('num_cadastral_code')
    def _compute_cadastral_code(self):
        for record in self:
            cadastral_code = ''
            if record.num_cadastral_code > 0:
                cadastral_code = str(record.num_cadastral_code).zfill(
                    self._size_cadastral_code)
            record.cadastral_code = cadastral_code

    def _compute_number_of_municipalities(self):
        for record in self:
            number_of_municipalities = 0
            if record.municipality_ids:
                number_of_municipalities = len(record.municipality_ids)
            record.number_of_municipalities = number_of_municipalities

    @api.constrains('num_cadastral_code')
    def _check_num_cadastral_code(self):
        max_cadastral_code = (10 ** self._size_cadastral_code) - 1
        for record in self:
            if record.num_cadastral_code > max_cadastral_code:
                raise exceptions.ValidationError(_('Code too big.'))

    def action_show_municipalities(self):
        self.ensure_one()
        current_province = self
        id_tree_view = self.env.ref(
            'base_loc.res_municipality_view_tree').id
        id_form_view = self.env.ref(
            'base_loc.res_municipality_view_form').id
        search_view = self.env.ref(
            'base_loc.res_municipality_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Municipalities'),
            'res_model': 'res.municipality',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree'), (id_form_view, 'form')],
            'search_view_id': (search_view.id, search_view.name),
            'target': 'current',
            'domain': [('province_id', '=', current_province.id)],
            'context': {'current_province_id': current_province.id, }
            }
        return act_window

    def _get_region(self):
        resp = 0
        regions = self.env['res.region'].search([])
        if regions and len(regions) == 1:
            resp = regions[0].id
        return resp
