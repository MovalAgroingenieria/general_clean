# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


class EomElectronicfileCommunication(models.Model):
    _inherit = 'eom.electronicfile.communication'

    res_letter_id = fields.Many2one(
        string='Registry',
        comodel_name='res.letter',
        readonly=True,
        ondelete='restrict',
        track_visibility='onchange')

    def action_show_res_letter_id(self):
        self.ensure_one()
        id_form_view = self.env.ref('crm_lettermgmt.res_letter_form_view').id
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Registry'),
            'res_model': 'res.letter',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(id_form_view, 'form')],
            'target': 'current',
            'res_id': self.res_letter_id.id
            }
        return act_window

    @api.model
    def create(self, vals):
        # Create the communication to get data and check draft state
        res = super(EomElectronicfileCommunication, self).create(vals)
        if vals['state'] == '01_draft':
            return res
        # Get parent electronic file data
        electronicfile = False
        electronicfile = self.env['eom.electronicfile'].browse(
            vals['electronicfile_id'])
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
        resgistry_issue = _('Electronic Communication %s') % vals['name']
        registry_date = vals['validation_time']
        # Create a new registry
        resgistry_note = _('Communication Issue: %s \n') % vals['issue']
        res_letter_vals = {
            'move': registry_move,
            'sender_partner_id': sender_partner_id.id,
            'recipient_partner_id': recipient_partner_id.id,
            'date': registry_date,
            'name': resgistry_issue,
            'note': resgistry_note,
            'state': 'sent', }
        registry = self.env['res.letter'].create(res_letter_vals)
        # Write the registry id in the communication
        res.write({'res_letter_id': registry.id})
        return res

    @api.multi
    def write(self, vals):
        if 'res_letter_id' in vals:
            return super(EomElectronicfileCommunication, self).write(vals)
        state = ""
        if 'state' in vals:
            state = vals['state']
        if state == '02_validated':
            # Get parent electronic file data
            electronicfile = False
            efile_id = self._context.get('active_id', False)
            if efile_id:
                electronicfile = self.env['eom.electronicfile'].browse(
                    efile_id)
            else:
                electronicfile = self.electronicfile_id
            # Get partner and company
            partner_id = company_id = False
            if electronicfile:
                partner_id = electronicfile.partner_id
                company_id = self.env.user.company_id
            if not partner_id or not company_id:
                raise exceptions.ValidationError(
                    _('Partner or Company not found, cannot create registry.'))
            # Notification (OUT)
            registry_move = 'out'
            sender_partner_id = company_id
            recipient_partner_id = partner_id
            resgistry_issue = _('Electronic Notification %s') % self.name
            registry_date = fields.datetime.now()
            # Create a new registry
            resgistry_note = _('Communication Issue: %s \n') % self.issue
            res_letter_vals = {
                'move': registry_move,
                'sender_partner_id': sender_partner_id.id,
                'recipient_partner_id': recipient_partner_id.id,
                'date': registry_date,
                'name': resgistry_issue,
                'note': resgistry_note,
                'state': 'sent', }
            registry = self.env['res.letter'].create(res_letter_vals)
            vals['res_letter_id'] = registry.id
        return super(EomElectronicfileCommunication, self).write(vals)
