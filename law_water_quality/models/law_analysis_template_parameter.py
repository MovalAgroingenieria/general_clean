# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class LawAnalysisTemplateParameterRel(models.Model):
    _name = 'law.analysis.template.parameter.rel'
    _description = 'Relation between Analysis Template and Parameter'
    _rec_name = 'parameter_id'

    analysis_template_id = fields.Many2one(
        string='Analysis Template',
        comodel_name='law.analysis.template',
        required=True,
        ondelete='cascade'
    )

    parameter_id = fields.Many2one(
        string='Parameter',
        comodel_name='law.parameter',
        required=True,
        ondelete='cascade',
        index=True,
    )

    uom_id = fields.Many2one(
        string='Unit of Measure',
        related='parameter_id.uom_id',
        store=True,
        readonly=True
    )
