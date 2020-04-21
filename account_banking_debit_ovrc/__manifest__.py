# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Debit OVRc",
    "summary": 'This module generate a normalized payment file for '
               'Castellon Virtual Collection Office (OVRc)',
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_banking_pain_base",
        "partner_second_lastname",
        "partner_address_street_number",
        "l10n_es_partner_address_street_type",
        "l10n_es_ine_code",
    ],
    "data": [
        "data/account_payment_method_data.xml",
        "views/account_payment_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
