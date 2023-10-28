# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Board Grafana Integration",
    "summary": "Grafana integration for board module",
    "version": "15.0.1.0.0",
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "board",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "views/board_grafana_view.xml",
        "views/base_menu.xml",
        "views/resources.xml",
    ],
    "installable": True,
    "application": False,
}
