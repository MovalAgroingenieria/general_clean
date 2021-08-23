# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "WauSMS client SMS",
    "summary": "Send SMS to one or several partners.",
    "version": '10.0.1.1.1',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "partner_mobile_buttons",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/wausms_view.xml",
        "views/res_partner_view.xml",
        "views/wausms_config_settings_view.xml",
        "data/wausms_config_settings_data.xml",
        "views/wausms_tracking_view.xml",
        "views/account_invoice_view.xml",
        "wizards/wausms_wizard_view.xml",
        "views/wausms_template_view.xml",
        "views/resources.xml",
    ],
    'external_dependencies': {
        'python': [
            'phonenumbers',
        ],
    },
    "installable": True,
    "application": False,
    "price": 10.0,
    "currency": "EUR",
    "images": ["static/description/banner.png"],
}
