# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Task Timer Self Edit",
    "summary": "Track and edit task time",
    "version": "14.0.1.0.0",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "category": "Human Resources/Attendances",
    "depends": [
        'project',
        'hr_timesheet',
        'analytic'
    ],
    "data": [
        'views/project_task_time.xml',
    ],
    "installable": True,
    "application": False,
}
