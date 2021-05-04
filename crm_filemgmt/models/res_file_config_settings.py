# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class FileConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.file.config.settings'
    _description = 'Configuration of File Management'

    default_annual_seq_prefix = fields.Char(
        string='Prefix (annual seq.)',
        size=10,
        help='Default Code for Files: <prefix>/<year>/num',
    )

    enable_access_file_filemgmt_portal_user = fields.Boolean(
        string='Enable access of portal user to file management',
        default=True,
        help='Grant or revoke access of portal users to file management',
    )

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('res.file.config.settings',
                           'default_annual_seq_prefix',
                           self.default_annual_seq_prefix)
        values.set_default('res.file.config.settings',
                           'enable_access_file_filemgmt_portal_user',
                           self.enable_access_file_filemgmt_portal_user)
        self.sudo().assign_permissions_on_resfile_to_portaluser(
            self.enable_access_file_filemgmt_portal_user)

    def assign_permissions_on_resfile_to_portaluser(
            self, enable_read_permission):
        group_portal = self.env.ref('base.group_portal', False)
        model_res_file = self.env['ir.model'].search(
            [('model', '=', 'res.file')])
        if group_portal and model_res_file:
            ir_model_access_for_resfile_portaluser = \
                self.env['ir.model.access'].search(
                    [('model_id', '=', model_res_file.id),
                        ('group_id', '=', group_portal.id)])
            if ir_model_access_for_resfile_portaluser:
                ir_model_access_for_resfile_portaluser.perm_read = \
                    enable_read_permission
