# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Audit Log Cron",
    "summary": "Cron jobs for audit log",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "auditlog",
    ],
    "data": [
        'data/ir_cron.xml',
    ],
    "installable": True,
    "application": False,
}
