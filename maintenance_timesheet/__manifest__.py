# -*- coding: utf-8 -*-
# Copyright 2019 Solvos Consultoría Informática (<http://www.solvos.es>)
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Maintenance Timesheets',
    'summary': 'Adds timesheets to maintenance request',
    'version': '10.0.1.1.1',
    'category': 'Human Resources',
    'website': 'http://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'maintenance_project',
        'hr_timesheet',
    ],
    'data': [
        'security/maintenance_timesheet_security.xml',
        'views/hr_timesheet_views.xml',
        'views/maintenance_request_views.xml',
    ],
    'demo': [
        'data/demo_maintenance_timesheet.xml',
    ],
    'installable': True,
    'application': False,
}
