# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'AEAT SII extradata',
    'version': '10.0.1.0.0',
    'category': 'Moval General Addons',
    'website': 'http://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'l10n_es_aeat_sii',
    ],
    'data': [
        'data/ir_config_parameter.xml',
        'data/aeat_sii_tax_agency_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
