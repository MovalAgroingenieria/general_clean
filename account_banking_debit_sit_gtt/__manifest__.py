# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Debit SIT GTT",
    "summary": "This module generate a normalized payment file for SIT GTT",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_banking_pain_base",
        "partner_second_lastname",
        "l10n_es_partner_address_street_type",
        "partner_address_street_number",
        "account_banking_communication_wizard",
    ],
    "data": [
        "data/account_payment_method_data.xml",
        "views/account_payment_line_views.xml",
        "views/account_payment_order_views.xml",
        "views/account_invoice_view.xml",
        "views/resources.xml",
    ],
    "installable": True,
    "application": False,
}
