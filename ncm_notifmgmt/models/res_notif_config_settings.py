# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResNotifConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.notif.config.settings'
    _description = 'Configuration of ncm_notifmgmt module'

    sequence_notificationset_code_id = fields.Many2one(
        string='Sequence for the codes of notification sets',
        comodel_name='ir.sequence',)

    default_notificationset_type_id = fields.Many2one(
        string='Default type for the notification sets',
        comodel_name='res.notificationset.type',)

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('res.notif.config.settings',
                           'sequence_notificationset_code_id',
                           self.sequence_notificationset_code_id.id)
        values.set_default('res.notif.config.settings',
                           'default_notificationset_type_id',
                           self.default_notificationset_type_id.id)
