# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Maintenance Projects',
    'summary': 'Adds projects to maintenance equipments and requests',
    'version': '10.0.1.0.1',
    'category': 'Maintenance',
    'website': 'http://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'maintenance',
        'project',
    ],
    'data': [
        'security/maintenance_project_security.xml',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_request_views.xml',
        'views/project_project_views.xml',
        #'report/maintenance_request_report.xml',
    ],
    'demo': [
        'data/demo_maintenance_project.xml',
    ],
    'installable': True,
    'application': False,
}
