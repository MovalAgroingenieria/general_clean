# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Attendances Staff Manager',
    'summary': 'Add the Staff manager group to the Attendance groups',
    'version': '10.0.1.0.1',
    'category': 'Human Resources',
    'website': 'http://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'hr_attendance',
    ],
    'data': [
        'security/hr_attendance_security.xml',
        'security/ir.model.access.csv',
        'views/hr_attendance_view.xml',
    ],
    'installable': True,
    'application': False,
}
