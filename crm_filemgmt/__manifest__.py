# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'File Management',
    'summary': 'Monitoring and file relationships',
    'version': '13.0.1.1.0',
    'category': 'Customer Relationship Management',
    'website': 'https://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'base_gen',
        'mail',
    ],
    'data': [
        'data/ir_module_category_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/crm_filemgmt_menus.xml',
        'views/res_config_settings_views.xml',
        'views/res_file_views.xml',
        'views/res_filetag_views.xml',
        'views/resources.xml',
        'views/res_file_category_views.xml',
        'views/res_partner_views.xml',
        'views/res_file_location_views.xml',
        'views/res_file_container_views.xml',
        'views/res_file_containertype_views.xml',
    ],
    "post_init_hook": "post_init_hook",
    'application': True,
    'installable': True,
}
