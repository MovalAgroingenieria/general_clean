# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    nrs_ids = fields.One2many(
        string="SMS's sent",
        comodel_name='nrs.tracking',
        inverse_name='invoice_id')

    num_sms_certified = fields.Integer(
        string="Number of SMS",
        compute="_compute_num_sms_certified")

    @api.multi
    def _compute_num_sms_certified(self):
        for record in self:
            record.num_sms_certified = len(record.nrs_ids)

    @api.multi
    def action_see_nrs_invoice(self):
        tree_view = \
            self.env.ref('nrs_client_sms.nrs_tracking_view_tree_invoice')
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
