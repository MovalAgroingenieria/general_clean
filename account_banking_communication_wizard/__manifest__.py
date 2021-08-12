# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Communitacion Wizard",
    "summary": "Wizard for communication field",
    "version": '10.0.1.1.0',
    "category": "Accounting",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "OPL-1",
    "depends": [
        "account_banking_pain_base",
    ],
    "data": [
        "views/account_payment_order_view.xml",
        "wizards/communication_wizard_view.xml",
    ],
    "installable": True,
    "application": False,
    "price": 10.0,
    "currency": "EUR",
}
