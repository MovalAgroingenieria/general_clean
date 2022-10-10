# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "AEAT modelo 347 non deductible taxes",
    'version': "10.0.1.1.2",
    'author': "Moval Agroingeniería",
    'website': "http://www.moval.es",
    'category': "Accounting",
    'license': "AGPL-3",
    'depends': [
        "l10n_es_aeat_mod347",
        "l10n_es_extradata",
    ],
    'data': [
        "data/tax_code_map_mod347_data.xml",
    ],
    'images':  ['static/description/banner.png'],
    'installable': True,
}
