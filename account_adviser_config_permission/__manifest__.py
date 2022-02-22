# -*- coding: utf-8 -*-
# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Adviser Config Permission",
    "summary": "Write permission config Adviser user",
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
        "security/ir.model.access.csv",
        "views/res_config_view.xml",
    ],
    "installable": True,
    "application": False,
}
