# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Configurable Upload Size',
    'version': '10.0.1.0.0',
    'category': 'Technical Settings',
    'summary': 'Configurable file upload size limit',
    'description': """
Configurable Upload Size
========================

This module allows configuring the maximum file upload size through
system parameters.

Features:
* Configurable maximum file upload size
* System parameter to control the limit
* JavaScript override to use dynamic upload size

Configuration:
* Go to Settings > Technical > System Parameters
* Set 'web.max_file_upload_size' parameter (value in MB)
* Default is 25 MB if not configured
    """,
    'author': 'Moval',
    'depends': ['base', 'web'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
