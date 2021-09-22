# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Partner extension for NRS'

    nrs_ids = fields.One2many(
        string="SMS's sent",
        comodel_name='nrs.tracking',
        inverse_name='partner_id')

    num_sms = fields.Integer(
        string="Number of SMS",
        compute="_compute_num_sms")

    show_icon_next_mobile = fields.Boolean(
        compute="_compute_show_icon_next_mobile")

    show_icon_on_partner_view_kanban = fields.Boolean(
        compute="_compute_show_icon_on_partner_view_kanban")


    @api.multi
    def _compute_num_sms(self):
        for record in self:
            record.num_sms = len(record.nrs_ids)

    @api.multi
    def action_see_nrs(self):
        tree_view = \
            self.env.ref('nrs_client_sms.nrs_tracking_view_tree_partner')
        form_view = self.env.ref('nrs_client_sms.nrs_tracking_view_form')
        return {
            'name': _('SMS'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'nrs.tracking',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': [('id', 'in', self.nrs_ids.ids)],
        }

    @api.multi
    def _compute_show_icon_next_mobile(self):
        show_icon_next_mobile = self.env['ir.values'].get_default(
                'nrs.configuration', 'show_icon_next_mobile')
        for record in self:
            record.show_icon_next_mobile = show_icon_next_mobile

    @api.multi
    def _compute_show_icon_on_partner_view_kanban(self):
        show_icon_on_partner_view_kanban = self.env['ir.values'].get_default(
                'nrs.configuration', 'show_icon_on_partner_view_kanban')
        for record in self:
            record.show_icon_on_partner_view_kanban = \
                show_icon_on_partner_view_kanban
