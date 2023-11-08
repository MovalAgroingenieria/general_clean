# -*- coding: utf-8 -*-
# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account User Group Field Modification",
    "summary": "Parter credit field can be viewed by account user group",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/account_security.xml",
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "application": False,
}
