# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Editable Description",
    "summary": "This module allows display and print the product description \
                instead of product name.",
    "version": '10.0.1.1.0',
    "category": "Moval Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "stock",
    ],
    "data": [
        "views/stock_pack_operation_views.xml",
        "report/stock_pack_operation_report_views.xml",
    ],
    "installable": True,
    "application": False,
}
