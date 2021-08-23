# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Cookie Notice External',
    'summary': """Insert a cookie URL service""",
    "version": '10.0.1.1.0',
    "category": "Tools",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        'website',
    ],
    "data": [
        "views/res_config_views.xml",
        "templates/website.xml",
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "application": False,
    "price": 5.0,
    "currency": "EUR",
}
