# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, exceptions, _



class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    stage_new = fields.Boolean(
        string="Stage: New",
        related='stage_id.is_new',
        readonly=True,
        store=False,
    )
    
    def write(self, vals):
        vals = vals or {}
        if 'stage_id' in vals:
            if not self.tag_ids and not self.source_id:
                raise exceptions.UserError(
                    _('You must indicate Category and Origin to the lead '
                      'before changing the stage.')
                )
        return super(CrmLead, self).write(vals)