# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Employee Attendances / Leaves Report",
    "summary": "Create a employee attendance/leaves report",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "http://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "hr_attendance",
        "hr_holidays",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/template_employee_attendance_views.xml",
        "wizard/employee_attendance_views.xml",
    ],
    "installable": True,
    "application": False,
    "price": 15.0,
    "currency": "EUR",
}

