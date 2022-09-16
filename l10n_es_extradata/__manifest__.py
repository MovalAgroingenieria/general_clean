# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "l10n_es_extradata",
    "version": "10.0.2.0.0",
    "author": "Moval",
    "website": 'https://moval.es',
    "category": "moval",
    "license": "AGPL-3",
    "depends": [
        "account",
        "l10n_es",
        "l10n_es_aeat_mod303",
        "l10n_es_aeat_mod347",
    ],
    "data": [
        "data/account_tax_group_data.xml",
        "data/taxes_common.xml",
        "data/tax_code_map_mod303_data.xml",
        "data/tax_code_map_mod347_data.xml",
        "views/account_view.xml",
    ],
    'installable': True,
}
