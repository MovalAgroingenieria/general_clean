# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Client Connect',
    'summary': 'Interest Collector for Odoo',
    'version': '10.0.1.1.1',
    'category': 'Moval General Addons',
    'website': 'http://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'auth_signup',
        'web',
    ],
    'data': [
        'views/login_view_extended.xml',
    ],
    'installable': True,
    'application': False,
}
