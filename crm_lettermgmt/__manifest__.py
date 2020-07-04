# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Letter Management',
    'summary': 'Track letters, parcels, registered documents',
    'version': '10.0.1.1.0',
    'category': 'Customer Relationship Management',
    'website': 'https://odoo-community.org/',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'mail'
    ],
    'data': [
        'views/res_letter_view.xml',
        'views/letter_category_view.xml',
        'views/letter_type_view.xml',
        'views/letter_channel_view.xml',
        'views/letter_folder_view.xml',
        'views/letter_reassignment_view.xml',
        'data/letter_sequence.xml',
        'security/ir.model.access.csv',
        'security/lettermgmt_security.xml',
        'views/resources.xml',
    ],
    'demo': ['data/letter_demo.xml'],
    'application': False,
    'installable': True,
}
