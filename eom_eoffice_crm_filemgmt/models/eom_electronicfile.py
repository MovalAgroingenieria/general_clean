# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, modules, exceptions, _


class EomElectronicfile(models.Model):
    _inherit = 'eom.electronicfile'

    file_id = fields.Many2one(
        string='File_',
        comodel_name='res.file',
        ondelete='restrict',
        track_visibility='onchange')

    def action_show_file_id(self):
        self.ensure_one()
        id_form_view = self.env.ref('crm_filemgmt.res_file_view_form').id
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('File_'),
            'res_model': 'res.file',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(id_form_view, 'form')],
            'target': 'current',
            'res_id': self.file_id.id
            }
        return act_window
