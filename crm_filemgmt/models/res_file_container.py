# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ResFileContainer(models.Model):
    _name = 'res.file.container'
    _description = "Container of Files"

    def _default_container_code(self):
        resp = 0
        file_containers = self.search(
            [('container_code', '>', 0)], limit=1, order='container_code desc')
        if len(file_containers) == 1:
            resp = file_containers[0].container_code + 1
        else:
            resp = 1
        return resp

    container_code = fields.Integer(
        string='Code',
        default=_default_container_code,
        required=True,
        index=True)

    name = fields.Char(
        string='Name',
        size=100,
        required=True,
        index=True)

    description = fields.Char(
        string='Description',
        size=255)

    location_id = fields.Many2one(
        string='Location',
        comodel_name='res.file.location',
        required=True,
        index=True,
        ondelete='restrict')

    image = fields.Binary(
        string='Photo / Image',
        attachment=True)

    file_ids = fields.One2many(
        string='Files',
        comodel_name='res.file',
        inverse_name='container_id')

    notes = fields.Html(
        string='Notes')

    number_of_files = fields.Integer(
        string='Files',
        store=True,
        compute='_compute_number_of_files')

    containertype_id = fields.Many2one(
        string='Type',
        comodel_name='res.file.containertype',
        index=True,
        ondelete='restrict')

    _sql_constraints = [
        ('unique_container_code', 'UNIQUE (container_code)',
         'Existing container code.'),
        ('container_code_positive', 'CHECK (container_code > 0 )',
         'The container code has to be positive.'),
        ('unique_name', 'UNIQUE (name)', 'Existing container name.')]

    @api.depends('file_ids')
    def _compute_number_of_files(self):
        for record in self:
            if record.file_ids:
                record.number_of_files = len(record.file_ids)

    @api.multi
    def action_get_files(self):
        self.ensure_one()
        if self.file_ids:
            id_tree_view = self.env.ref('crm_filemgmt.'
                                        'res_file_view_tree_related').id
            id_form_view = self.env.ref('crm_filemgmt.res_file_view_form').id
            search_view = self.env.ref('crm_filemgmt.res_file_view_search')
            act_window = {
                'type': 'ir.actions.act_window',
                'name': _('Files'),
                'res_model': 'res.file',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(id_tree_view, 'tree'),
                          (id_form_view, 'form')],
                'search_view_id': (search_view.id, search_view.name),
                'target': 'current',
                'domain': [('id', 'in', self.file_ids.ids)],
                }
            return act_window

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if self.env.context.get('show_container_data', False):
                if record.location_id:
                    name += _(' [location: ') + record.location_id.name + ']'
                if record.containertype_id:
                    name += _(' [type: ') + record.containertype_id.name + ']'
            result.append((record.id, name))
        return result


class ResFileContainerType(models.Model):
    _name = 'res.file.containertype'
    _description = "Type of containers"

    name = fields.Char(
        string='Name',
        size=100,
        required=True,
        index=True)

    description = fields.Char(
        string='Description',
        size=255)

    notes = fields.Html(
        string='Notes')

    _sql_constraints = [
        ('unique_container_type', 'UNIQUE (name)',
         'Existing container type.')]
