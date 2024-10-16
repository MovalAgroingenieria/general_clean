# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResEomConfigSettings(models.TransientModel):
    _inherit = 'res.eom.config.settings'

    sequence_electronicfile_code_id = fields.Many2one(
        string='Sequence for the codes of electronic files',
        comodel_name='ir.sequence',
        help='Default values of the electronic file codes',)

    deadline = fields.Integer(
        string='Deadline (months)',
        default=3,
        help='Number of months for resolution within the deadline.')

    @api.multi
    def set_default_values(self):
        super(ResEomConfigSettings, self).set_default_values()
        values = self.env['ir.values'].sudo()
        values.set_default('res.eom.config.settings',
                           'sequence_electronicfile_code_id',
                           self.sequence_electronicfile_code_id.id)
        values.set_default('res.eom.config.settings',
                           'deadline', self.deadline)
