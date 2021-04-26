# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Debit External Collector",
    "summary": 'Marks the invoices sent to an external collector',
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_banking_pain_base",
        "account_banking_communication_wizard",
    ],
    "data": [
        "data/account_payment_method_data.xml",
        "views/resources.xml",
        "views/account_invoice_view.xml",
        "views/account_payment_line_views.xml",
        "views/account_view.xml",
    ],
    "installable": True,
    "application": False,
}
