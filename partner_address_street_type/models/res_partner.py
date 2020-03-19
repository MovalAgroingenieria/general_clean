# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _default_street_type_id(self):
        resp = 0
        proposed_street_type_id = \
            self.env['res.street.type'].search(
                [('is_default', '=', True), ('show_in_list', '=', True)])
        if proposed_street_type_id:
            resp = proposed_street_type_id[0].id
        return resp

    street_type_id = fields.Many2one(
        string='Street type',
        comodel_name='res.street.type',
        ondelete="set null")

    street_type_show = fields.Char(
        string="Street type show",
        compute="_compute_street_type_show")

    @api.multi
    def _compute_street_type_show(self):
        config_type_shown = self.env['ir.values'].get_default(
                'res.street.type.configuration', 'street_type_shown')
        for record in self:
            street_type_show = ''
            if record.street_type_id:
                if config_type_shown == 'long':
                    street_type_show = record.street_type_id.name
                elif config_type_shown == 'short':
                    street_type_show = record.street_type_id.abbreviation
                else:
                    street_type_show = ""
            record.street_type_show = street_type_show

    @api.model
    def _address_fields(self):
        fields = super(ResPartner, self)._address_fields()
        fields.append('street_type_id')
        fields.append('street_type_show')
        return fields

    @api.model
    def create(self, vals):
        if 'street_type_id' in vals:
            config_type_shown = self.env['ir.values'].get_default(
                'res.street.type.configuration', 'street_type_shown')
            street_type_id = vals.get('street_type_id')
            street_type = self.env['res.street.type'].browse(street_type_id)
            if config_type_shown == 'long':
                vals['street_type_show'] = street_type.name
            elif config_type_shown == 'short':
                vals['street_type_show'] = street_type.abbreviation
            else:
                vals['street_type_show'] = ""
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'street_type_id' in vals:
            config_type_shown = self.env['ir.values'].get_default(
                'res.street.type.configuration', 'street_type_shown')
            street_type_id = vals.get('street_type_id')
            street_type = self.env['res.street.type'].browse(street_type_id)
            if config_type_shown == 'long':
                vals.update({'street_type_show': street_type.name,})
            elif config_type_shown == 'short':
                vals.update({'street_type_show': street_type.abbreviation,})
            else:
                vals.update({'street_type_show': "",})
        return super(ResPartner, self).write(vals)
