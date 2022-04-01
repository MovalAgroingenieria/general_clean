# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Address Street Type",
    "summary": "This module add street type to partner address (base module).",
    "version": '14.0.1.1.0',
    "category": "Partner Management",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "contacts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "views/res_street_type_views.xml",
        "views/res_partner_views.xml",
        "views/res_street_type_menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
}
