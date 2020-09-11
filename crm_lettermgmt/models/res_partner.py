# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    recipient_res_letter_ids = fields.One2many(
        string='Registry as recipient',
        comodel_name='res.letter',
        inverse_name='recipient_partner_id')

    number_of_registers_as_recipent = fields.Integer(
        string='Num. registers as recipient',
        compute='_compute_number_of_registers_as_recipent')

    sender_res_letter_ids = fields.One2many(
        string='Registry as sender',
        comodel_name='res.letter',
        inverse_name='sender_partner_id')

    number_of_registers_as_sender = fields.Integer(
        string='Num. registers as sender',
        compute='_compute_number_of_registers_as_sender')

    total_res_letter_ids = fields.One2many(
        string='Registry',
        comodel_name='res.letter',
        compute='_compute_total_res_letter_ids')

    number_of_total_registers = fields.Integer(
        string='Num. registers',
        compute='_compute_number_of_total_registers')

    @api.multi
    def _compute_number_of_registers_as_recipent(self):
        for record in self:
            record.number_of_registers_as_recipent = \
                len(record.recipient_res_letter_ids)

    @api.multi
    def _compute_number_of_registers_as_sender(self):
        for record in self:
            record.number_of_registers_as_sender = \
                len(record.sender_res_letter_ids)

    @api.multi
    def _compute_number_of_total_registers(self):
        for record in self:
            record.number_of_total_registers = len(record.total_res_letter_ids)

    @api.multi
    def action_get_registers(self):
        self.ensure_one()
        if self.recipient_res_letter_ids:
            id_tree_view = self.env.ref('crm_lettermgmt.'
                                        'res_letter_tree_o2m_view').id
            id_form_view = self.env.ref('crm_lettermgmt.'
                                        'res_letter_form_view').id
            search_view = self.env.ref('crm_lettermgmt.res_letter_filter')
            act_window = {
                'type': 'ir.actions.act_window',
                'name': _('Registers'),
                'res_model': 'res.letter',
                'view_type': 'form',
                'view_mode': 'tree',
                'views': [(id_tree_view, 'tree'),
                          (id_form_view, 'form')],
                'search_view_id': (search_view.id, search_view.name),
                'target': 'current',
                'domain': [('id', 'in', self.total_res_letter_ids.ids)],
                }
            return act_window

    @api.depends('recipient_res_letter_ids', 'sender_res_letter_ids')
    def _compute_total_res_letter_ids(self):
        for record in self:
            total_res_letter_ids = []
            if record.recipient_res_letter_ids:
                for recipient_res_letter_id in record.recipient_res_letter_ids:
                    total_res_letter_ids.append(recipient_res_letter_id.id)
            if record.sender_res_letter_ids:
                for sender_res_letter_id in record.sender_res_letter_ids:
                    total_res_letter_ids.append(sender_res_letter_id.id)
            record.total_res_letter_ids = total_res_letter_ids
