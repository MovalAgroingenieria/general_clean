# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Electronic Office File Management',
    'summary': 'Link electronic files and communications with CRM modules',
    'version': '10.0.1.0.0',
    'category': 'Electronic Offices Management',
    'website': 'http://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'eom_eoffice',
        'crm_filemgmt',
    ],
    'data': [
        'views/eom_electronicfile_view.xml',
        'views/eom_electronicfile_communication_view.xml',
        'views/res_partner_view.xml',
        'views/res_letter_view.xml',
        'views/res_file_view.xml',
        'reports/res_letter_report.xml',
    ],
    'installable': True,
    'application': False,
}
