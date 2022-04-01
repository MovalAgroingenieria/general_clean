# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResFileContainerType(models.Model):
    _name = 'res.file.containertype'
    _description = "Type of containers"
    _inherit = 'simple.model'

    _size_name = 30
    _size_description = 100
    _set_num_code = False

    alphanum_code = fields.Char(
        string='Name',
        required=True,
        index=True,)
