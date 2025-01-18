# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class GisviewerLayer(models.Model):
    _name = "gisviewer.layer"
    _description = "GIS Viewer Layer"
    _order = "name"

    _sql_constraints = [
        ('unique_code', 'UNIQUE (code)',
         'Technical Code must be unique.'),
    ]

    name = fields.Char(
        string="Layer",
        translate=True,
    )

    code = fields.Char(
        string="Technical Code",
        required=True,
    )

    layerprofile_ids = fields.One2many(
        string='Layer Profiles',
        comodel_name='gisviewer.layer.profile',
        inverse_name='gisviewer_layer_id',
    )

    notes = fields.Html(
        string='Internal Notes',
    )

    @api.multi
    def action_get_available_profiles(self):
        profiles = self.env['gisviewer.profile'].search([])
        for profile in profiles:
            # Only one group layer relation
            layer_already_config = self.layerprofile_ids and len(
                self.layerprofile_ids.filtered(
                    lambda x: x.gisviewer_profile_id.code == profile.code))
            if (not layer_already_config):
                self.env['gisviewer.layer.profile'].create({
                    'gisviewer_layer_id': self.id,
                    'gisviewer_profile_id': profile.id,
                })


class GisviewerLayerProfile(models.Model):
    _name = 'gisviewer.layer.profile'

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)',
         'Existing Layer Profile Relation.'),
        ]

    name = fields.Char(
        string='GIS Layer Profile Relation',
        store=True,
        compute='_compute_name',
        index=True,
    )

    gisviewer_layer_id = fields.Many2one(
        string='GIS Layer',
        comodel_name='gisviewer.layer',
        required=True,
        index=True,
        ondelete='cascade',
    )

    gisviewer_profile_id = fields.Many2one(
        string='GIS Profile',
        comodel_name='gisviewer.profile',
        required=True,
        index=True,
        ondelete='cascade',
    )

    visible_public = fields.Boolean(
        string='Visible Public?',
        default=True,
    )

    active_public = fields.Boolean(
        string='Active Public?',
        default=True,
    )

    visible_private = fields.Boolean(
        string='Visible Private?',
        default=True,
    )

    active_private = fields.Boolean(
        string='Active Private?',
        default=True,
    )

    @api.onchange('visible_public')
    def _change_active_state_public(self):
        for record in self:
            if (not record.visible_public):
                record.active_public = False

    @api.onchange('visible_private')
    def _change_active_state_private(self):
        for record in self:
            if (not record.visible_private):
                record.active_private = False

    @api.depends('gisviewer_layer_id', 'gisviewer_layer_id.code',
                 'gisviewer_profile_id', 'gisviewer_profile_id.code',)
    def _compute_name(self):
        for record in self:
            value = ''
            if record.gisviewer_layer_id and record.gisviewer_profile_id:
                value = record.gisviewer_layer_id.code + '-' + \
                    record.gisviewer_profile_id.code
            record.name = value
