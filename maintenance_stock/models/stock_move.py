# -*- coding: utf-8 -*-
# Copyright 2019 Solvos Consultoría Informática (<http://www.solvos.es>)
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    maintenance_request_id = fields.Many2one(
        comodel_name="maintenance.request",
        related="picking_id.maintenance_request_id",
    )

    maintenance_equipment_id = fields.Many2one(
        comodel_name="maintenance.equipment",
        related="picking_id.maintenance_equipment_id",
    )
