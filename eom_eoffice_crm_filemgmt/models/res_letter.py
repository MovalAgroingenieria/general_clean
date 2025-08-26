# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ResLetter(models.Model):
    _inherit = 'res.letter'

    created_by_authdnie = fields.Boolean(
        string='Created by AuthDNIe',
        default=False,
        readonly=True)

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        ondelete='restrict',
        store=True,
        index=True,
        compute='_compute_company_id',
    )

    @api.depends('number', 'file_id')
    def _compute_company_id(self):
        company_id = self.env.user.company_id
        for record in self:
            electronicfile = self.env['eom.electronicfile'].sudo().search(
                [('file_id', '=', record.id)])
            if electronicfile:
                company_id = electronicfile.company_id
            record.company_id = company_id

    @api.model
    def create(self, vals):
        res_letter = super(ResLetter, self).create(vals)
        if vals.get('company_id'):
            res_letter.company_id = vals['company_id']
        return res_letter
