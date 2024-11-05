# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import hashlib
import json

from odoo.addons.web.controllers.main import module_boot
from odoo.addons.web.controllers.main import HomeStaticTemplateHelpers
from odoo.http import request
from odoo.tools import ustr

from odoo import models


class HttpProjectLimited(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(HttpProjectLimited, self).session_info()
        if (self.env.user.has_group('base.group_user') or
           self.env.user.has_group(
                'project_limited_access.group_portal_project_user')):
            user = request.env.user
            user_context = \
                request.session.get_context() if request.session.uid else {}
            mods = module_boot()
            qweb_checksum = \
                HomeStaticTemplateHelpers.get_qweb_templates_checksum(
                    addons=mods, debug=request.session.debug)
            lang = user_context.get("lang")
            translation_hash = \
                request.env['ir.translation'].get_web_translations_hash(
                    mods, lang)
            menu_json_utf8 = json.dumps(request.env['ir.ui.menu'].load_menus(
                request.session.debug), default=ustr, sort_keys=True).encode()
            cache_hashes = {
                "load_menus": hashlib.sha512(menu_json_utf8).hexdigest()[:64],
                "qweb": qweb_checksum,
                "translations": translation_hash,
            }
            session_info.update({
                "user_companies":
                    {'current_company':
                        (user.company_id.id, user.company_id.name),
                        'allowed_companies': [(comp.id, comp.name)
                                              for comp in user.company_ids]},
                "currencies": self.get_currencies(),
                "show_effect": True,
                "display_switch_company_menu": (user.has_group(
                    'base.group_multi_company') and len(user.company_ids) > 1),
                "cache_hashes": cache_hashes,
            })
        return session_info
