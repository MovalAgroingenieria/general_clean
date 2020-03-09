# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Banking Debit ATRM",
    "summary": "This module generate a normalized payment file for \
               'Tax Agency of the Region of Murcia (ATRM)'",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account_banking_pain_base",
        "partner_second_lastname",
        "partner_street_type",
        "l10n_es_ine_code",
    ],
    "data": [
        "data/account_payment_method_data.xml",
        "reports/atrm_resume.xml",
        "views/account_invoice_view.xml",
        "views/account_payment_line_views.xml",
        "views/account_payment_order_views.xml",
        "views/resources.xml",
    ],
    "installable": True,
    "application": False,
}
