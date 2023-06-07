# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from datetime import datetime
import pytz


class CustomIrCron(models.Model):
    _inherit = 'ir.cron'

    excluded_days = fields.Char(
        string='Excluded days',
        help='Comma separated of days to exclude on execution',
    )

    @api.multi
    def method_direct_trigger(self):
        for record in self:
            if (record.excluded_days):
                days_to_exclude = [
                    int(x) for x in record.excluded_days.split(',')]
                tz = record.user_id.tz or 'Europe/Madrid'
                timezone_user = pytz.timezone(tz)
                today = datetime.now(timezone_user).day
                if (today not in days_to_exclude):
                    super(CustomIrCron, self).method_direct_trigger()
            else:
                super(CustomIrCron, self).method_direct_trigger()
