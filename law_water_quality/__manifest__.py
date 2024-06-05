# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Laboratory Analysis for Waters',
    'summary': 'Manage the analysis of water samples from laboratories',
    'version': '10.0.1.1.0',
    'category': 'Laboratory Analysis for Waters',
    'website': 'https://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'contacts',
        'mail',
    ],
    'data': [
        'security/law_water_quality_security.xml',
        'security/ir.model.access.csv',
        'views/resources.xml',
        'views/law_analysis_view.xml',
        'views/law_analysis_parameter_view.xml',
        'views/law_parameter_uom_view.xml',
        'views/law_parameter_view.xml',
        'views/law_water_quality_menus.xml',
        'views/law_watertype_view.xml',
        'views/law_water_quality_menus.xml',
        'reports/law_analysis_report.xml',
    ],
    'application': False,
    'installable': True,
}
