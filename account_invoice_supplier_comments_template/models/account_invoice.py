# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    supplier_comment_template1_id = fields.Many2one(
        'base.comment.template', string='Top Comment Template')

    supplier_comment_template2_id = fields.Many2one(
        'base.comment.template', string='Bottom Comment Template')

    note_supp1ier1 = fields.Html('Top Comment')

    note_supp1ier2 = fields.Html('Bottom Comment')


    @api.onchange('supplier_comment_template1_id')
    def _set_note_supp1ier1(self):
        comment = self.supplier_comment_template1_id
        if comment:
            self.note_supp1ier1 = comment.get_value(self.partner_id.id)

    @api.onchange('supplier_comment_template2_id')
    def _set_note_supp1ier2(self):
        comment = self.supplier_comment_template2_id
        if comment:
            self.note_supp1ier2 = comment.get_value(self.partner_id.id)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res2 = super(AccountInvoice, self)._onchange_partner_id()
        supplier_comment_template = \
            self.partner_id.supplier_comment_template_id
        if supplier_comment_template.position == 'before_lines':
            self.supplier_comment_template1_id = supplier_comment_template
        elif supplier_comment_template.position == 'after_lines':
            self.supplier_comment_template2_id = supplier_comment_template
        return res2


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_comment_template_id = fields.Many2one(
        comodel_name='base.comment.template',
        string='Supplier conditions template')

    @api.model
    def _commercial_fields(self):
        res2 = super(ResPartner, self)._commercial_fields()
        res2 += ['supplier_comment_template_id']
        return res2

