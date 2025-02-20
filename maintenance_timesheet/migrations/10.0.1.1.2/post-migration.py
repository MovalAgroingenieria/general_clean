# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref(
        'maintenance_timesheet.hr_timesheet_rule_request_user',
        raise_if_not_found=False,
    )
    if rule:
        rule.unlink()
    rule = env.ref(
        'maintenance_timesheet.hr_timesheet_rule_request_manager',
        raise_if_not_found=False,
    )
    if rule:
        rule.unlink()
