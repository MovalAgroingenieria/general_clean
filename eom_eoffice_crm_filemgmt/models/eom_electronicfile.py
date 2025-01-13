# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class EomElectronicfile(models.Model):
    _inherit = 'eom.electronicfile'

    file_id = fields.Many2one(
        string='File_',
        comodel_name='res.file',
        ondelete='restrict',
        track_visibility='onchange')

    has_associated_file = fields.Boolean(
        string='Has associated file',
        store=True,
        compute='_compute_has_associated_file')

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

    @api.multi
    def write(self, vals):
        # Add communication registries as file registries
        res = super(EomElectronicfile, self).write(vals)
        if 'file_id' in vals:
            file = self.env['res.file'].browse(vals['file_id'])
            file_res_letter_ids = []
            communication_ids = self.env[
                'eom.electronicfile.communication'].search(
                    [('electronicfile_id', '=', self.id)])
            for communication in communication_ids:
                if communication.res_letter_id:
                    file_res_letter_ids.append(communication.res_letter_id.id)
            if file_res_letter_ids:
                for id in file_res_letter_ids:
                    file.file_res_letter_ids = [(4, id)]
        return res

    @api.depends('file_id')
    def _compute_has_associated_file(self):
        for record in self:
            record.has_associated_file = bool(record.file_id)
