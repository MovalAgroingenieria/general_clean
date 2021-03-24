# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Attendances Self Edit",
    "summary": "Track and edit employee attendance",
    "version": "13.0.1.0.0",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "category": "Human Resources/Attendances",
    "depends": [
        "hr_attendance",
        "hr_employee_firstname",
    ],
    "data": [
        "security/security.xml",
        "views/hr_attendance_view.xml",
        "views/custom_views.xml",
    ],
    "installable": True,
    "application": False,
}
