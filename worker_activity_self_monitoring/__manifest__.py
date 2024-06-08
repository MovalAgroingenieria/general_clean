# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Worker Activity Self Monitoring",
    "summary": "Worker will be able to monitor his own activity.",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "author": "Moval Agroingeniería",
    "website": "http://www.moval.es",
    "category": "Human Resources/Attendance",
    "depends": [
        "web",
        "hr_attendance",
        "bus",
    ],
    "data": [
        "views/resources.xml",
    ],
    'qweb': [
        'static/src/xml/tray_icons_template.xml',
    ],
    "application": False,
    "installable": True,
    "uninstall_hook": "uninstall_hook",
}
