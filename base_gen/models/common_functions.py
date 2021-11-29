# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import locale
from odoo import models, fields, api


class CommonFunctions(models.AbstractModel):
    _name = 'common.functions'
    _description = 'Common functions to be used by other models'

    @api.model
    def transform_float_to_locale(self, float_number, precision, lang=True):
        if lang != True:
            report_lang = str(lang + '.utf8')
        else:
            report_lang = str(self.env.context['lang'] + '.utf8')
        locale.setlocale(locale.LC_NUMERIC, report_lang)
        precision = '%.' + str(precision) + 'f'
        formated_float_number = locale.format(precision, float_number, True)
        locale.resetlocale(locale.LC_NUMERIC)
        return formated_float_number
