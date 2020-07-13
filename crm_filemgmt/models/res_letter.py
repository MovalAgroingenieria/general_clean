# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResLetter(models.Model):
    _inherit = 'res.letter'

    file_id = fields.Many2one(
        string='File',
        comodel_name='res.file',
        ondelete='restrict',
        track_visibility='onchange')
