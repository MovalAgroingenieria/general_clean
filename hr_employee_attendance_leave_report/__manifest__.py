# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Employee Attendances / Leaves Report",
    "summary": "Create a employee attendance/leaves report",
    "version": '13.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "hr_attendance_with_lastnames",
        "hr_holidays",
        "hr_holidays_public",
        "web_fontawesome",
    ],
    "data": [
        "wizard/hr_employee_attendance_leave_wizard_views.xml",
        "report/hr_employee_attendance_leave_report_views.xml",
        "views/resources.xml",
    ],
    "installable": True,
    "application": False,
}

