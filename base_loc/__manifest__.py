# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Localization Management",
    "summary": "Localization based on a hierarchy of territories "
               "(regions, provinces and municipalities)",
    "version": "15.0.1.0.0",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "category": "Hidden",
    "installable": True,
    "application": False,
    "depends": [
        "base_gen",
    ],
    "data": [
        "views/res_region_views.xml",
        "views/res_province_views.xml",
        "views/res_municipality_views.xml",
        "views/res_place_views.xml",],
    "assets": {
        "web.assets_backend": [
            "/base_loc/static/src/css/base_loc.css",
        ],
        "web.assets_frontend": [
        ],
        "web.assets_qweb": [
        ],
        "web.report_assets_common": [
        ],
    },

}