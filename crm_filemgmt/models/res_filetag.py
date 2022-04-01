# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResFiletag(models.Model):
    _name = 'res.filetag'
    _description = 'Tags for files'
    _inherit = 'simple.model'

    _size_name = 30
    _set_num_code = False
    _set_alphanum_code_to_lowercase = False
    _set_alphanum_code_to_uppercase = False

    alphanum_code = fields.Char(
        string='File Tag',
        required=True,
        translate=True,)

    color = fields.Integer(
        string='Color Index',
        help='0:no-color, 1:red, 2:orange, 3:yellow, 4:Cyan, 5:dark-purple, '
             '6:pink, 7:blue, 8:dark-blue, 9:magenta, 10:green, 11:purple')
