# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "GIS Viewer Management",
    "summary": "Management of data related to the gis viewer infrastructure.",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "https://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/gisviewer_profile_data.xml",
        "views/resources.xml",
        "views/base_menu.xml",
        "views/gisviewer_layer_view.xml",
        "views/gisviewer_profile_view.xml",
    ],
    "installable": True,
    "application": False,
}
