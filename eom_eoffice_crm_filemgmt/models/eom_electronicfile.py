# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


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

    res_letter_id = fields.Many2one(
        string='Registry',
        comodel_name='res.letter',
        readonly=True,
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

    @api.model
    def create(self, vals):
        vals['res_letter_id'] = False
        res = super(EomElectronicfile, self).create(vals)
        # Get electronic file data
        electronicfile = self
        # Get partner and company
        partner_id = company_id = False
        if electronicfile:
            partner_id = electronicfile.partner_id
            company_id = self.env.user.company_id
        if not partner_id or not company_id:
            raise exceptions.ValidationError(
                _('Partner or Company not found, cannot create registry.'))
        # Communication (IN)
        registry_move = 'in'
        sender_partner_id = partner_id
        recipient_partner_id = company_id
        resgistry_issue = _('New Electronic file %s') % electronicfile.name
        registry_date = electronicfile.event_time
        # Create a new registry
        resgistry_note = _('Electronic file type %s \n') % electronicfile.type
        res_letter_vals = {
            'move': registry_move,
            'sender_partner_id': sender_partner_id.id,
            'recipient_partner_id': recipient_partner_id.id,
            'date': registry_date,
            'name': resgistry_issue,
            'note': resgistry_note,
            'state': 'sent',
            'created_by_authdnie': True,
        }
        registry = self.env['res.letter'].create(res_letter_vals)
        # Write the registry id in the communication
        res.write({'res_letter_id': registry.id})
        # Add registry to file_id
        file_id = electronicfile.file_id or False
        if file_id:
            file_id.file_res_letter_ids = [(4, registry.id)]
        return res
