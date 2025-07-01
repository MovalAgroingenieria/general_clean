# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class EomDigitalregister(models.Model):
    _inherit = 'eom.digitalregister'

    # Overwrite parent method to create partner if it does not exist
    @api.model
    def create_access(self, dni, firstname, lastname, authority):
        if dni and firstname and lastname and authority:
            digitalregister = self.search([('name', '=', dni)])
            if not digitalregister:
                vals = {
                    'name': dni,
                    'firstname': firstname,
                    'lastname': lastname,
                    'authority': authority,
                    }
                digitalregister = self.create(vals)
            else:
                digitalregister = digitalregister[0]
                vals = {}
            model_digitalregister_access = \
                self.env['eom.digitalregister.access']
            new_access = model_digitalregister_access.create({
                'digitalregister_id': digitalregister.id, })
            model_res_partner = self.env['res.partner']
            existing_partner = model_res_partner.search(
                [('vat', '=', dni)], limit=1)
            if existing_partner:
                if not digitalregister.partner_id:
                    digitalregister.write({'partner_id': existing_partner.id})
            else:
                fullname = lastname + ' ' + firstname
                vals_partner = {
                    'name': fullname,
                    'vat': dni,
                    'created_by_authdnie': True,
                }
                partner_id = model_res_partner.create(vals_partner).id
                digitalregister.write({'partner_id': partner_id})
            return new_access
        else:
            return False
