# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResFile(models.Model):
    _inherit = 'res.file'

    has_associated_electronicfile = fields.Boolean(
        string='Has associated electronic file',
        store=True,
        compute='_compute_has_associated_electronicfile')

    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        ondelete='restrict',
        store=True,
        index=True,
        compute='_compute_company_id',
    )

    @api.depends('file_res_letter_ids')
    def _compute_company_id(self):
        company_id = self.env.user.company_id
        for record in self:
            if record.file_res_letter_ids:
                company_id = record.file_res_letter_ids[:1].company_id
            record.company_id = company_id

    @api.multi
    def _compute_has_associated_electronicfile(self):
        for record in self:
            has_associated_electronicfile = False
            associated_electronicfile = self.env['eom.electronicfile'].search(
                [('file_id', '=', record.id)])
            if associated_electronicfile:
                has_associated_electronicfile = True
                record.has_associated_electronicfile = \
                    has_associated_electronicfile
