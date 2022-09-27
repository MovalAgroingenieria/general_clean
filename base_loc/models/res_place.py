# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ResPlace(models.Model):
    _name = 'res.place'
    _description = 'Place'
    _inherit = 'simple.model'

    _size_name = 50
    _set_num_code = False
    _set_alphanum_code_to_lowercase = False
    _set_alphanum_code_to_uppercase = False

    def _default_municipality_id(self):
        resp = 0
        current_municipality_id = \
            self.env.context.get('current_municipality_id', False)
        if current_municipality_id:
            resp = current_municipality_id
        return resp

    alphanum_code = fields.Char(
        string='Place',
        required=True,
        translate=True,)

    municipality_id = fields.Many2one(
        string='Municipality',
        comodel_name='res.municipality',
        default=_default_municipality_id,
        required=True,
        index=True,
        ondelete='restrict',)

    province_id = fields.Many2one(
        string='Province',
        comodel_name='res.province',
        store=True,
        index=True,
        compute='_compute_province_id',)

    region_id = fields.Many2one(
        string='Region',
        comodel_name='res.region',
        store=True,
        index=True,
        compute='_compute_region_id',)

    @api.depends('municipality_id', 'municipality_id.province_id')
    def _compute_province_id(self):
        for record in self:
            province_id = None
            if record.municipality_id:
                province_id = record.municipality_id.province_id
            record.province_id = province_id

    @api.depends('province_id', 'province_id.region_id')
    def _compute_region_id(self):
        for record in self:
            region_id = None
            if record.province_id:
                region_id = record.province_id.region_id
            record.region_id = region_id
