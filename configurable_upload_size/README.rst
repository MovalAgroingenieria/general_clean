.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Configurable Upload Size
=========================

Description
===========

This module allows configuring the maximum file upload size in Odoo through 
system parameters, replacing the fixed 25 MB limit hardcoded in Odoo's core.

Features
--------

* **Configurable size**: Upload limit can be adjusted dynamically.
* **System parameter**: Uses ``ir.config_parameter`` to store configuration.
* **JavaScript override**: Overrides FieldBinary widget behavior.
* **Default value**: 25 MB if not configured.

Installation
============

#. Copy the module to the addons folder.
#. Update the modules list.
#. Install the *Configurable Upload Size* module.

Configuration
=============

#. Go to **Settings > Technical > System Parameters**.
#. Search or create the parameter: ``web.max_file_upload_size``.
#. Set the value in MB (example: ``50`` for 50 MB).
#. Save changes.

Usage
=====

Once configured, all binary fields (files, images) will use the new size limit.

System Parameters
-----------------

========================  =========================================  ==============
Key                       Description                                Default Value
========================  =========================================  ==============
``web.max_file_upload_size``  Maximum upload size in MB               25
========================  =========================================  ==============

Technical Notes
===============

* The value is automatically converted from MB to bytes.
* If parameter retrieval fails, uses 25 MB as fallback.
* Compatible with Odoo 10.0.

Credits
=======

* Moval Agroingeniería S.L.

Contributors
------------

* Guillermo Amante <gamante@moval.es>
* Samuel Fernández <sfernandez@moval.es>
* Pablo García <pgarcia@moval.es>
* Alberto Hernández <ahernandez@moval.es>
* Eduardo Iniesta <einiesta@moval.es>
* Jesús Martínez <jmartinez@moval.es>
* Miguel Mora <mmora@moval.es>
* Miguel Ángel Rodríguez <marodriguez@moval.es>
* Juanu Sandoval <jsandoval@moval.es>
* Salvador Sánchez <ssanchez@moval.es>
* Jorge Vera <jvera@moval.es>

Maintainer
----------

.. image:: https://services.moval.es/static/images/logo_moval_small.png
   :target: http://moval.es
   :alt: Moval Agroingeniería

This module is maintained by Moval Agroingeniería.
