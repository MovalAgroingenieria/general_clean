# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    # Payment comment templates
    paymentorder_comment_template1_id = fields.Many2one(
        'base.comment.template',
        string='Top Comment Template')

    paymentorder_comment_template2_id = fields.Many2one(
        'base.comment.template',
        string='Bottom Comment Template')

    # Payment order note HTML fields
    note_paymentorder1 = fields.Html(
        string='Top comment',
        translate=True)

    note_paymentorder2 = fields.Html(
        string='Bottom comment',
        translate=True)

    @api.onchange('paymentorder_comment_template1_id')
    def _set_note_paymentorder1(self):
        comment = self.paymentorder_comment_template1_id
        if comment:
            self.note_paymentorder1 = comment.get_value(self.partner_id.id)

    @api.onchange('paymentorder_comment_template2_id')
    def _set_note_paymentordee2(self):
        comment = self.paymentorder_comment_template2_id
        if comment:
            self.note_paymentorder2 = comment.get_value(self.partner_id.id)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountPaymentOrder, self).onchange_partner_id()
        paymentorder_comment_template = \
            self.partner_id.paymentorder_comment_template_id
        if paymentorder_comment_template.position == 'before_lines':
            self.paymentorder_comment_template1_id = \
                paymentorder_comment_template
        elif paymentorder_comment_template.position == 'after_lines':
            self.paymentorder_comment_template2_id = \
                paymentorder_comment_template
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Payment order comments
    paymentorder_comment_template_id = fields.Many2one(
        comodel_name='base.comment.template',
        string='Payment order comment template')

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res += ['paymentorder_comment_template_id']
        return res
