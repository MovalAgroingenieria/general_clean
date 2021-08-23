# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Audit Log Cron Vacuum - Admin",
    "summary": "Cron job for cleaning records of the audit log owned by the "
               "admin user",
    "version": '10.0.1.1.0',
    "category": "Productivity",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "auditlog",
    ],
    "data": [
        'data/ir_cron.xml',
    ],
    'images': ["static/description/banner.png",
               "images/moval.png"
    ],
    "installable": True,
    "application": False,
}
