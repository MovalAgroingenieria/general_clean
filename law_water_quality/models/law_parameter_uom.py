# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class LawParameterUom(models.Model):
    _name = "law.parameter.uom"
    _description = "Law Parameter Unit of Measure"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )

    short_name = fields.Char(
        string="Short Name",
        index=True,
    )

    description = fields.Char(
        string="Description",
    )

    parameter_ids = fields.One2many(
        comodel_name="law.parameter",
        inverse_name="uom_id",
        string="Parameters",
    )

    notes = fields.Html(
        string="Notes",
    )

    sql_constraints = [
        ("name_unique", "unique(name)",
         "The unit of measure must be unique."),
        ("short_name_unique", "unique(short_name)",
         "The unit of measure must be unique.")
    ]

    def name_get(self):
        result = []
        for record in self:
            name = record.name or ""
            short_name = record.short_name or ""
            display_name = "{} ({})".format(name, short_name)
            result.append((record.id, display_name))
        return result

    @api.multi
    def action_see_parameters(self):
        self.ensure_one()
        condition = [('uom_id', '=', self.id)]
        id_tree_view = self.env.ref(
            'law_water_quality.law_parameter_view_tree').id
        search_view = self.env.ref(
            'law_water_quality.law_parameter_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Parameters'),
            'res_model': 'law.parameter',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree')],
            'search_view_id': (search_view.id, search_view.name),
            'domain': condition,
            'target': 'current',
            'context': '{\'create\': False, \'edit\': False}',
        }
        return act_window
