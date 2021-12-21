# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'File Management',
    'summary': 'Monitoring and file relationships',
    'version': '10.0.1.1.0',
    'category': 'Customer Relationship Management',
    'website': 'https://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'crm_lettermgmt',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/res_file_category_data.xml',
        'views/crm_filemgmt_menus.xml',
        'views/res_file_config_settings_view.xml',
        'views/res_file_view.xml',
        'views/res_filetag_view.xml',
        'views/resources.xml',
        'views/res_file_category_view.xml',
        'views/res_partner_view.xml',
        'views/res_letter_view.xml',
        'views/res_file_location_view.xml',
        'views/res_file_container_view.xml',
        'views/res_company_view.xml',
    ],
    'application': False,
    'installable': True,
}
