# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def migrate(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rule = env.ref(
        "hr_attendance_staff_manager."
        "hr_attendance_rule_attendance_staff_manager",
        raise_if_not_found=False
    )
    if rule:
        domain = (
            "['|', ('employee_id.user_id', '=', user.id), "
            " '|', ('employee_id', '=', False), "
            "      ('employee_id', 'in', user.employee_ids and "
            "       user.employee_ids[0].child_ids.ids or [0])]"
        )
        rule.write({'domain_force': domain})
