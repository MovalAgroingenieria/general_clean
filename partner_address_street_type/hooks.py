# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):
    # Add street type to address format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(street)s',
        E'%(street_type_show)s %(street)s'
        )
    """
    try:
        cr.execute(query)
    except Exception:
        pass


def uninstall_hook(cr, registry):
    # Remove street type from address format
    query = """
        UPDATE res_country
        SET address_format = replace(
        address_format,
        E'%(street_type_show)s',
        ''
        )
    """
    try:
        cr.execute(query)
    except Exception:
        pass
