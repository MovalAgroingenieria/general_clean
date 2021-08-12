# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Credit Control Variable Fees",
    "summary": "Add variable fees to credit control",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_credit_control_dunning_fees",
        "account_credit_control_html",
    ],
    "data": [
        "views/control_credit_policy_view.xml",
        "reports/report_credit_control_summary.xml",
    ],
    "installable": True,
    "application": False,
    "price": 10.0,
    "currency": "EUR",
}
