# -*- coding: utf-8 -*-
# Copyright 2019 Solvos Consultoría Informática (<http://www.solvos.es>)
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    def _prepare_project_from_equipment_values(self, values):
        data = super(MaintenanceEquipment,
                     self)._prepare_project_from_equipment_values(values)
        data['allow_timesheets'] = True
        return data
