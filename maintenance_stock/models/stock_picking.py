# -*- coding: utf-8 -*-
# Copyright 2019 Solvos Consultoría Informática (<http://www.solvos.es>)
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    maintenance_request_id = fields.Many2one(
        comodel_name="maintenance.request",
        index=True,
    )

    maintenance_equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        related="maintenance_request_id.equipment_id",
    )
