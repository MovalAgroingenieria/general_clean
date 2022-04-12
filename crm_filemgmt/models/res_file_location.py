# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ResFileLocation(models.Model):
    _name = 'res.file.location'
    _description = "Locations of Files"
    _inherit = 'simple.model'

    _size_name = 6
    _size_description = 100
    _set_num_code = True

    num_code = fields.Integer(
        string='Code',
        required=True,
        index=True,)

    long_name = fields.Char(
        string='Name',
        size=100,
        required=True,
        index=True,)

    location_id = fields.Many2one(
        string='Site',
        comodel_name='res.file.location',
        ondelete='restrict',)

    image = fields.Image(
        string='Photo / Image',)

    container_ids = fields.One2many(
        string='Containers',
        comodel_name='res.file.container',
        inverse_name='location_id',)

    number_of_containers = fields.Integer(
        string='Files',
        store=True,
        compute='_compute_number_of_containers',)

    @api.depends('container_ids')
    def _compute_number_of_containers(self):
        for record in self:
            if record.container_ids:
                record.number_of_containers = len(record.container_ids)

    def name_get(self):
        resp = []
        for record in self:
            name = record.long_name
            if record.num_code:
                name += ' [' + str(record.num_code) + ']'
            resp.append((record.id, name))
        return resp

    def action_get_containers(self):
        self.ensure_one()
        if self.container_ids:
            id_tree_view = self.env.ref(
                'crm_filemgmt.res_file_container_view_tree_related').id
            id_form_view = self.env.ref(
                'crm_filemgmt.res_file_container_view_form').id
            search_view = self.env.ref(
                'crm_filemgmt.res_file_container_view_search')
            act_window = {
                'type': 'ir.actions.act_window',
                'name': _('Containers'),
                'res_model': 'res.file.container',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(id_tree_view, 'tree'),
                          (id_form_view, 'form')],
                'search_view_id': (search_view.id, search_view.name),
                'target': 'current',
                'domain': [('id', 'in', self.container_ids.ids)],
                }
            return act_window
