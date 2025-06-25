# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        # If it's an internal note without a model,
        # clear recipients to avoid sending
        subtype = \
            self.sudo().env['mail.message.subtype'].browse(
                vals.get('subtype_id'))
        if (subtype and subtype.internal and not vals.get('model') and
                vals.get('partner_ids')):
            vals['partner_ids'] = [(6, 0, [])]
        return super(MailMessage, self).create(vals)
