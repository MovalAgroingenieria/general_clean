# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import locale
from odoo import models, api


class CommonFunctions(models.AbstractModel):
    _name = 'common.functions'
    _description = 'Common functions to be used by other models'

    @api.model
    def transform_float_to_locale(self, float_number, precision, lang=False):
        final_lang = str(self.env.context['lang'] + '.utf8')
        if lang:
            final_lang = str(lang + '.utf8')
        locale.setlocale(locale.LC_NUMERIC, final_lang)
        precision = '%.' + str(precision) + 'f'
        formated_float_number = locale.format(precision, float_number, True)
        locale.resetlocale(locale.LC_NUMERIC)
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
