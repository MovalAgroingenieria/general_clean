# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MDM Sensor Management',
    'summary': 'Measurement Devices and Sensors Management',
    'version': '10.0.1.1.0',
    'category': 'Tools',
    'website': 'https://www.moval.es',
    'author': 'Moval Agroingeniería',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/resources.xml',
        'views/measurement_device_views.xml',
        'views/measurement_device_sensor_reading_views.xml',
        'views/measurement_device_sensor_type_views.xml',
        'views/measurement_device_sensor_uom_views.xml',
        'views/measurement_device_sensor_views.xml',
        'views/mdm_menus.xml',
    ],
    'application': False,
    'installable': True,
}
