# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Odoo Mobile App Blog",
    "summary": "Mobile App to connect with Odoo Blog",
    "version": '10.0.1.0.0',
    "category": "Mobile",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        'odoo_mobile_app',
        'website_blog',
    ],
    "data": [
        "views/resources.xml",
        "views/oma_notification_set_view.xml",
        "views/oma_notification_view.xml",
    ],
    "installable": True,
    "application": True,
}
