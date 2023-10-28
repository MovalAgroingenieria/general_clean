# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Localization Management",
    "summary": "Localization based on a hierarchy of territories "
               "(regions, provinces and municipalities)",
    "version": "15.0.1.0.0",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "category": "Hidden",
    "depends": [
        "base_gen",
    ],
    "data": [
        "views/resources.xml",
        "views/res_region_views.xml",
        "views/res_province_views.xml",
        "views/res_municipality_views.xml",
        "views/res_place_views.xml",],
    "installable": True,
    "application": False,
}