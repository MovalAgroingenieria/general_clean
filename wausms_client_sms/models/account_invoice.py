# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    wausms_ids = fields.One2many(
        string="SMS's sent",
        comodel_name='wausms.tracking',
        inverse_name='invoice_id')

    num_sms = fields.Integer(
        string="Number of SMS",
        compute="_compute_num_sms")

    @api.multi
    def _compute_num_sms(self):
        for record in self:
            record.num_sms = len(record.wausms_ids)

    @api.multi
    def action_see_wausms_invoice(self):
        tree_view = \
            self.env.ref('wausms_client_sms.wausms_tracking_view_tree_invoice')
        form_view = self.env.ref('wausms_client_sms.wausms_tracking_view_form')
        return {
            'name': _('SMS'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'wausms.tracking',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': [('id', 'in', self.wausms_ids.ids)],
        }
