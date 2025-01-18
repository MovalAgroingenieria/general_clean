# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


class GisviewerProfile(models.Model):
    _name = "gisviewer.profile"
    _description = "GIS Viewer Profile"
    _order = "name"

    _sql_constraints = [
        ('unique_code', 'UNIQUE (code)',
         'Technical Code must be unique.'),
    ]

    name = fields.Char(
        string="GIS Profile",
        translate=True,
    )

    code = fields.Char(
        string="Technical Code",
        required=True,
    )

    layerprofile_ids = fields.One2many(
        string='Layer Profiles',
        comodel_name='gisviewer.layer.profile',
        inverse_name='gisviewer_profile_id',
    )

    notes = fields.Html(
        string='Internal Notes',
    )

    is_readonly = fields.Boolean(
        string="Readonly",
        required=True,
        default=False,
    )

    user_ids = fields.One2many(
        string='Users',
        comodel_name='res.users',
        inverse_name='gisviewer_profile_id',
    )

    @api.multi
    def unlink(self):
        for record in self:
            if record.is_readonly:
                raise exceptions.UserError(
                    _('It is not possible to remove system profiles.'))
        res = super(GisviewerProfile, self).unlink()
        return res

    @api.multi
    def action_get_available_layers(self):
        layers = self.env['gisviewer.layer'].search([])
        for layer in layers:
            # Only one group layer relation
            layer_already_config = self.layerprofile_ids and len(
                self.layerprofile_ids.filtered(
                    lambda x: x.gisviewer_layer_id.code == layer.code))
            if (not layer_already_config):
                self.env['gisviewer.layer.profile'].create({
                    'gisviewer_layer_id': layer.id,
                    'gisviewer_profile_id': self.id,
                })
