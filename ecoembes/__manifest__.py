# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Ecoembes",
    "summary": "Add Ecoembes contribution management",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "category": "Tools",
    "version": "14.0.0.0.0",
    "depends": ["account"],
    "data": [
        'data/product_material.xml',
        'data/product_submaterial.xml',
        'data/submaterial_types.xml',
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/product_material_view.xml",
        "views/product_submaterial_view.xml",
        "views/submaterial_type_view.xml",
        "views/product_template_view.xml",
        "views/menu.xml",
        "report/report_invoice_scrap_notice.xml",
    ],
    "application": False,
    "installable": True,
}
