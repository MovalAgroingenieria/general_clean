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

#     file_res_letter_ids = fields.One2many(
#         string='File registry',
#         comodel_name='res.letter',
#         inverse_name='file_id',
#         compute='_compute_file_res_letter_ids')
# 
#     number_of_file_registers = fields.Integer(
#         string='Num. file registers',
#         compute='_compute_number_of_file_registers')

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

#     def _compute_number_of_file_registers(self):
#         for record in self:
#             record.number_of_file_registers = len(record.file_res_letter_ids)
# 
#     def action_get_file_registers(self):
#         self.ensure_one()
#         if self.file_res_letter_ids:
#             id_tree_view = self.env.ref('crm_lettermgmt.'
#                                         'res_letter_tree_o2m_view').id
#             id_form_view = self.env.ref('crm_lettermgmt.'
#                                         'res_letter_form_view').id
#             search_view = self.env.ref('crm_lettermgmt.res_letter_filter')
#             act_window = {
#                 'type': 'ir.actions.act_window',
#                 'name': _('File registers'),
#                 'res_model': 'res.letter',
#                 'view_mode': 'tree',
#                 'views': [(id_tree_view, 'tree'),
#                           (id_form_view, 'form')],
#                 'search_view_id': (search_view.id, search_view.name),
#                 'target': 'current',
#                 'domain': [('id', 'in', self.file_res_letter_ids.ids)],
#                 }
#             return act_window
# 
#     @api.depends('file_ids')
#     def _compute_file_res_letter_ids(self):
#         for record in self:
#             partner_file_ids = []
#             registers_of_partner = []
#             if record.file_ids:
#                 for partner_file_id in record.file_ids:
#                     partner_file_ids.append(partner_file_id.file_id.id)
#             if len(partner_file_ids) > 0:
#                 registers_of_partner = self.env['res.letter'].search(
#                     [('file_id.id', 'in', partner_file_ids)])
#             if registers_of_partner:
#                 record.file_res_letter_ids = registers_of_partner
