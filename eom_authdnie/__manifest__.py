# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "DNIe-based Authentication",
    "summary": "Authentication for the frontend based on DNIe.",
    "version": '10.0.1.0.0',
    "category": "Electronic Offices Management",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "contacts",
        "mail",
        "website",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "wizards/wizard_set_vat_view.xml",
        "views/resources.xml",
        "views/eom_digitalregister_templates.xml",
        "views/res_partner_view.xml",
        "views/eom_authdnie_menus.xml",
        "views/res_eom_config_settings_view.xml",
        "views/eom_digitalregister_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "application": True,
}
