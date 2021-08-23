# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice Supplier Comments Template",
    "summary": "Add two comment HTML fields to supplier invoices",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "views/account_invoice_view.xml",
        "reports/report_invoice.xml",
    ],
    "installable": True,
    "application": False,
    "images": ["static/description/banner.png"],
}
