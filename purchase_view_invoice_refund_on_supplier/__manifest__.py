# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Purchase View Invoice Refund On Supplier',
    'summary': 'Add invoice refund on supplier',
    'version': '10.0.1.0.0',
    'category': 'Product Management',
    'website': 'https://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'purchase',
    ],
    'data': [
        'views/res_partner_view.xml',
    ],
}
