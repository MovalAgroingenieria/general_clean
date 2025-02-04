# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class DocumentPage(models.Model):
    _inherit = 'document.page'

    _TLDV_ENDPOINT_URL = 'https://pasta.tldv.io/v1alpha1/meetings'

    allowed_portal_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Visible to',
        store=True,
        readonly=False,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            project_id = vals.get('project_id')
            if project_id:
                project = self.env['project.project'].browse(project_id)
                if project.privacy_visibility == 'portal':
                    vals['allowed_portal_user_ids'] = [
                        (6, 0, project.allowed_portal_user_ids.ids)]
        return super().create(vals_list)

    def write(self, vals):
        if 'project_id' in vals or 'allowed_portal_user_ids' not in vals:
            for record in self:
                project = record.project_id
                if vals.get('project_id'):
                    project = self.env['project.project'].browse(
                        vals['project_id'])
                if project and project.privacy_visibility == 'portal':
                    vals['allowed_portal_user_ids'] = [
                        (6, 0, project.allowed_portal_user_ids.ids)]
        return super().write(vals)

    def _get_document_page_from_tldv(self):
        pass
