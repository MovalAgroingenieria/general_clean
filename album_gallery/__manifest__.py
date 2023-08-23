# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Album Gallery',
    'summary': """Show an album gallery  """,
    "version": '14.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "website",
        "mail",
    ],
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "data/album_gallery_menu_views.xml",
        "views/album_gallery_view.xml",
        "views/album_gallery_website_template.xml",
    ],
    "auto_install": False,
    "installable": True,
    "price": 50,
    "currency": "EUR"
}
