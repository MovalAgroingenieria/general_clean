# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import locale
from odoo import models, api


class CommonFunctions(models.AbstractModel):
    _name = 'common.functions'
    _description = 'Common functions to be used by other models'

    def transform_float_to_locale(self, float_number, precision):
        precision = '%.' + str(precision) + 'f'
        lang = 'es_ES'
        if ('lang' in self.env.context and self.env.context['lang']):
            lang = self.env.context['lang']
        lang_model = self.env['res.lang'].search([('code', '=', lang)])
        formated_float_number = str(float_number)
        if (lang_model):
            formated_float_number = \
                lang_model.format(precision, float_number, True)
        return formated_float_number

    def get_value_from_translation(self, module, src, lang=None):
        resp = src
        if not lang:
            lang = self.env.context.get('lang')
        filtered_translations = self.sudo().env['ir.translation'].search(
            [('lang', '=', lang), ('module', '=', module), ('src', '=', src)])
        if filtered_translations:
            resp = filtered_translations[0].value
        return resp
