# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Notification Management",
    "summary": "Notification management from the company to all the partners.",
    "version": '10.0.1.1.0',
    "category": "Notices and Correspondence",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "contacts",
        "mail",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "reports/res_notification_report.xml",
        "data/mail_template_data.xml",
        "data/res_notificationset_type_data.xml",
        "data/ir_sequence_data.xml",
        "data/res_notificationset_pdfs_cron.xml",
        "views/resources.xml",
        "views/ncm_notifmgmt_menus.xml",
        "views/res_notif_config_settings_view.xml",
        "views/res_notificationset_type_view.xml",
        "views/res_notificationset_view.xml",
        "views/res_notification_view.xml",
        "views/res_partner_view.xml",
        "wizard/wizard_preview_notification_view.xml",
    ],
    'qweb': ['static/src/xml/ncm_notifmgmt.xml'],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "application": True,
}
