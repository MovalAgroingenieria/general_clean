# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    company_filemgmt_annual_seq_prefix = fields.Char(
        string='Prefix (annual seq.)',
        size=10,
        help='Company code prefix for Files: <prefix>/<year>/num')

    is_multi_company = fields.Boolean(
        string='Is multicompany',
        default=False,
        compute="_compute_is_multi_company")

    current_user_id = fields.Many2one(
        string="User id",
        comodel_name="res.users",
        compute="_compute_current_user_id")

    @api.multi
    def _compute_is_multi_company(self):
        is_multi_company = \
            self.env['res.users'].has_group('base.group_multi_company')
        for record in self:
            record.is_multi_company = is_multi_company

    @api.multi
    def _compute_current_user_id(self):
        current_user_id = self.env.user.id
        for record in self:
            record.current_user_id = current_user_id
