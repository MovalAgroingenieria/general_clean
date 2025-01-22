# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Project Limited Access",
    "summary": "This module adds new group for .",
    "version": '14.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "web",
        "project",
        "sh_task_time",
        "mail",
        "mail_tracking",
        "prt_mail_messages_pro",
        "rating",
        "sale_timesheet",
        "hr_timesheet",
        "maintenance",
        "base_search_custom_field_filter",
        "moval_odoo_management",
        "odoo_user_login_security",
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_timesheet_views.xml',
        'views/project_views.xml',
        'views/project_task_views.xml',
        'views/mail_menus.xml',
        'views/maintenance_views.xml',
    ],
    "installable": True,
    "application": False,
}
