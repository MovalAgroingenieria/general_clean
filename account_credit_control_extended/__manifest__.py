# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Credit Control Extended",
    "summary": "Add custom fields to Credit Control",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_credit_control",
    ],
    "data": [
        "wizard/wizard_massive_line_description_change.xml",
        "views/credit_control_run.xml",
        "views/credit_control_line.xml",
    ],
    "installable": True,
    "application": False,
}
