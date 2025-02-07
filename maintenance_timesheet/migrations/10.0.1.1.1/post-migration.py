# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    _logger = logging.getLogger(__name__)
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref(
        'maintenance_timesheet.hr_timesheet_rule_request_user',
        raise_if_not_found=False,
    )
    if rule:
        rule.write({
            'domain_force': "[('maintenance_request_id', '!=', False)]",
        })
        _logger.info("Updated domain for hr_timesheet_rule_request_user")
        maintenance_group = env.ref(
            'base_maintenance_config.group_maintenance_user',
            raise_if_not_found=False,
        )
        if maintenance_group:
            rule.write({
                'groups': [(6, 0, [maintenance_group.id])],
            })
            _logger.info("Group maintenance.group_maintenance_user"
                         "set for hr_timesheet_rule_request_user.")
        else:
            _logger.warning(
                "Group maintenance.group_maintenance_user not found.")
    else:
        _logger.warning("hr_timesheet_rule_request_user not found")
    rule = env.ref(
        'maintenance_timesheet.hr_timesheet_rule_request_manager',
        raise_if_not_found=False,
    )
    if rule:
        rule.write({
            'domain_force': "[('maintenance_request_id', '!=', False)]",
        })
        _logger.info("Updated domain for hr_timesheet_rule_request_manager")
        maintenance_group = env.ref(
            'base_maintenance_config.group_maintenance_manager',
            raise_if_not_found=False,
        )
        if maintenance_group:
            rule.write({
                'groups': [(6, 0, [maintenance_group.id])],
            })
            _logger.info("Group maintenance.group_maintenance_manager"
                         "set for hr_timesheet_rule_request_manager.")
