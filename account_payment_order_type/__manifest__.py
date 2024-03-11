# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Payment Order Type",
    "summary": "Diff payment order or debit order report",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_payment_order",
        "base_wua_invoicing",
    ],
    "data": [
        "reports/account_payment_order.xml",
    ],
    "installable": True,
    "application": False,
    "images": ["static/description/banner.png"],
}
