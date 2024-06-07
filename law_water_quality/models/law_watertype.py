# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class LawWatertype(models.Model):
    _name = "law.watertype"
    _description = "Law Watertype"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )

    description = fields.Char(
        string="Description",
        index=True,
    )

    analysis_ids = fields.One2many(
        comodel_name="law.analysis",
        inverse_name="watertype_id",
        string="Analysis",
    )

    notes = fields.Html(
        string="Notes",
    )

    sql_constraints = [
        ("name_unique", "unique(name)",
         "The water type must be unique!"),
    ]

    @api.multi
    def action_see_analysis(self):
        self.ensure_one()
        condition = [('watertype_id', '=', self.id)]
        id_tree_view = self.env.ref(
            'law_water_quality.law_analysis_view_tree').id
        search_view = self.env.ref(
            'law_water_quality.law_analysis_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Analysis'),
            'res_model': 'law.analysis',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(id_tree_view, 'tree')],
            'search_view_id': (search_view.id, search_view.name),
            'domain': condition,
            'target': 'current',
            'context': '{\'create\': False, \'edit\': False}',
        }
        return act_window
