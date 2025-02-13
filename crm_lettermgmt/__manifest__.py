# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Letter Management',
    'summary': 'Track letters, parcels, registered documents',
    'version': '10.0.1.1.4',
    'category': 'Customer Relationship Management',
    'website': 'https://odoo-community.org/',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'mail'
    ],
    'data': [
        'security/lettermgmt_security.xml',
        'security/ir.model.access.csv',
        'data/letter_sequence.xml',
        'views/resources.xml',
        'views/res_letter_view.xml',
        'views/letter_category_view.xml',
        'views/letter_type_view.xml',
        'views/letter_channel_view.xml',
        'views/letter_folder_view.xml',
        'views/letter_reassignment_view.xml',
        'views/res_partner_view.xml',
        'views/res_letter_config_settings_view.xml',
        'reports/res_letter_report.xml',
        'data/res_letter_mail.xml',
        'wizards/res_letter_mail_wizard.xml',
    ],
    'demo': ['data/letter_demo.xml'],
    'application': False,
    'installable': True,
}
