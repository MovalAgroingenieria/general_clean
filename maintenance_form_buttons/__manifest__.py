# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Maintenance Form Buttons',
    'summary': 'Module used for adding a button box general to '
               'maintenance forms',
    'version': '10.0.1.1.0',
    'category': 'Mail',
    'website': 'https://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'maintenance',
    ],
    'data': [
        'views/maintenance_request_views.xml',
    ],
    'application': False,
    'installable': True,
}
