# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "HR attendance GIS Management",
    "summary": "Management of gis data related to the attendances.",
    "version": '10.0.1.1.0',
    "category": "Moval General Addons",
    "website": "https://www.moval.es",
    "author": "Moval Agroingeniería",
    "license": "AGPL-3",
    "depends": [
        "hr_attendance_geolocate",
    ],
    "data": [
        'views/hr_attendance.xml',
    ],
    "installable": True,
    "application": False,
}
