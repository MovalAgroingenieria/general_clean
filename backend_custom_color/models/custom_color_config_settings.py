# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.tools as tools
import os


class CustomColorConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'res.custom.theme.color.settings'

    backend_primary_color = fields.Char(
        string="Backend primary color",
        help="The backend theme primary color")

    @api.multi
    def set_default_values(self):
        values = self.env['ir.values'].sudo()
        values.set_default('res.custom.theme.color.settings',
                           'backend_primary_color', self.backend_primary_color)
        hexcolor = self.backend_primary_color
        varless_file = False
        addons_path = tools.config['addons_path'].split(',')
        for path in addons_path:
            if '/other_addons'in path:
                path = os.path.dirname(path)
                varless_file = path + '/backend_theme_v10/static/src/less/'\
                    'variables.less'
                varless_file_new = path + '/backend_theme_v10/static/src/'\
                    'less/variables_new.less'
        if varless_file:
            with open(varless_file) as fin, \
                    open(varless_file_new, 'w') as fout:
                for line in fin:
                    lineout = line
                    if line.startswith('@brand-primary:'):
                        lineout = "@brand-primary:         %s;\n" % hexcolor
                    if line.startswith('@brand-info:'):
                        lineout = "@brand-info:            %s;\n" % hexcolor
                    fout.write(lineout)
            fout.close()
            os.rename(varless_file_new, varless_file)
