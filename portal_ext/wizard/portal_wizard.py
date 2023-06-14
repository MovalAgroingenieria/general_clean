# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError
from odoo import api, fields, models, _


class PortalWizard(models.TransientModel):
    _inherit = 'portal.wizard'

    send_email = fields.Boolean(
        string="Send email",
        default=True,
        help="If checked, an invitation email will be sent.")

    @api.onchange('portal_id')
    def onchange_portal_id(self):
        partner_ids = self.env.context.get('active_ids', [])
        contact_ids = set()
        user_changes = []
        for partner in self.env['res.partner'].sudo().browse(partner_ids):
            if partner.id not in contact_ids:
                contact_ids.add(partner.id)
                in_portal = True
                if partner.user_ids:
                    in_portal = \
                        self.portal_id in partner.user_ids[0].groups_id
                user_changes.append((0, 0, {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'in_portal': in_portal}))
        self.user_ids = user_changes


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    @api.multi
    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        error_msg = self.get_error_messages()
        if error_msg:
            raise UserError("\n\n".join(error_msg))
        for wizard_user in self.sudo().with_context(active_test=False):
            group_portal = wizard_user.wizard_id.portal_id
            if not group_portal.is_portal:
                raise UserError(
                    _('Group %s is not a portal') % group_portal.name)
            user = wizard_user.partner_id.user_ids[0] \
                if wizard_user.partner_id.user_ids else None
            if wizard_user.partner_id.email != wizard_user.email:
                wizard_user.partner_id.write({'email': wizard_user.email})
            if wizard_user.in_portal:
                user_portal = None
                if not user:
                    if wizard_user.partner_id.company_id:
                        company_id = wizard_user.partner_id.company_id.id
                    else:
                        company_id = self.env['res.company'].\
                            _company_default_get('res.users').id
                    user_portal = wizard_user.sudo().with_context(
                        company_id=company_id)._create_user()
                else:
                    user_portal = user
                wizard_user.write({'user_id': user_portal.id})
                if (not wizard_user.user_id.active or group_portal not in
                        wizard_user.user_id.groups_id):
                    wizard_user.user_id.write(
                        {'active': True,
                         'groups_id': [(4, group_portal.id)]})
                    wizard_user.user_id.partner_id.signup_prepare()
                    if wizard_user.wizard_id.send_email:
                        wizard_user.with_context(
                            active_test=True)._send_email()
                wizard_user.refresh()
            else:
                if user and group_portal in user.groups_id:
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal.id)],
                                    'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal.id)]})
