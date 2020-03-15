.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Partner Addresss Street Type
============================

Description
===========

This module add street type field to the partner address fields. The street type is shown before the street field
in views and printable documents. How the street type field is shown (full street type name, abbreviation or not shown)
is set in "/Settings/Street Type Management/Settings" (by default it is set to "Not show").

To display the street type in the direction of the printable documents, the variable address_format has been modified
by adding the field before the street field and will be apply to all countries. However this order can changed in
street type settings (for all countries) or for each country in "Sales/Configuration/Contacts/Localization/Countries".

The types of street and their abbreviations are dependent on each country, so this is a base module that introduces the
model and the views, the data must be provided by another module.


Credits
=======

* Moval Agroingeniería S.L.

Contributors
------------

* Alberto Hernández <ahernandez@moval.es>
* Eduardo Iniesta <einiesta@moval.es>
* Miguel Mora <mmora@moval.es>
* Juanu Sandoval <jsandoval@moval.es>
* Salvador sánchez <ssanchez@moval.es>
* Jorge Vera <jvera@moval.es>

Maintainer
----------

.. image:: http://moval.es/wp-content/uploads/2017/01/LOGO-MOVAL-2017_HOME-e1483490247394.png
   :target: http://moval.es
   :alt: Moval Agroingeniería

This module is maintained by Moval Agroingeniería.
