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
