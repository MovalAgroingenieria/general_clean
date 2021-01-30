# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    file_ids = fields.One2many(
        string='Associated Files',
        comodel_name='res.file.partnerlink',
        inverse_name='partner_id')

    number_of_files = fields.Integer(
        string='Num. of files',
        compute='_compute_number_of_files')

    def _compute_number_of_files(self):
        for record in self:
            number_of_files = 0
            partnerlinks_of_partner = \
                self.sudo().env['res.file.partnerlink'].search(
                    [('partner_id', '=', record.id)])
            if partnerlinks_of_partner:
                number_of_files = len(partnerlinks_of_partner)
            record.number_of_files = number_of_files

    def action_get_files(self):
        self.ensure_one()
        if self.file_ids:
            id_tree_view = \
                self.env.ref('crm_filemgmt.'
                             'res_file_partnerlink_of_partner_view_tree').id
            search_view = \
                self.env.ref('crm_filemgmt.res_file_partnerlink_view_search')
            act_window = {
                'type': 'ir.actions.act_window',
                'name': _('File Partnerlinks'),
                'res_model': 'res.file.partnerlink',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(id_tree_view, 'tree')],
                'search_view_id': (search_view.id, search_view.name),
                'target': 'current',
                'domain': [('id', 'in', self.file_ids.ids)],
                }
            return act_window
