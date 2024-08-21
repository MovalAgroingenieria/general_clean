.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Account Banking Debit DipuCR
============================

Description
===========

This module generate a normalized payment file for 'Tax management. Ciudad Real
County Council (DipuCR)'.

Notes
=====
After installation, it is mandatory:

* create a payment mode called 'DipuCR' associated with the payment method Tax
  management. Ciudad Real County Council (DipuCR)'.

* configure the entity code in /Accounting/Configuration/Configuration section
  "Tax management. Ciudad Real County Council (DipuCR)"


It is also advisable not to use the option "Group transactions in payment
orders", in the configuration options of the DipuCR payment mode
(each transaction will be a bank payment line).

Credits
=======

* Moval Agroingeniería S.L.

Contributors
------------

* Ana Bernal <abernal@dipucr.es>
* Alberto Hernández <ahernandez@moval.es>
* Eduardo Iniesta <einiesta@moval.es>
* Miguel Mora <mmora@moval.es>
* Juanu Sandoval <jsandoval@moval.es>
* Salvador Sánchez <ssanchez@moval.es>
* Jorge Vera <jvera@moval.es>

Maintainer
----------

.. image:: https://services.moval.es/static/images/logo_moval_small.png
   :target: http://moval.es
   :alt: Moval Agroingeniería

This module is maintained by Moval Agroingeniería.
