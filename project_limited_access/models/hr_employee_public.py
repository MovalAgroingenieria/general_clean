# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    # Added fields because is included in log, but not inherits from
    # mail_thread so errors on module prt_mail_messages_pro
    hide_notifications = fields.Boolean(
        string="Hide notifications",
        help="Hide notifications",
    )

    hide_notes = fields.Boolean(
        string="Hide notes",
        help="Hide notes",
    )

    hide_messages = fields.Boolean(
        string="Hide messages",
        help="Hide messages",
    )
