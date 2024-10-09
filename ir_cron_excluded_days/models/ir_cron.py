# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta


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

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        """ Run a given job taking care of the repetition.

        :param job_cr: cursor to use to execute the job, safe to
         commit/rollback
        :param job: job to be run (as a dictionary).
        :param cron_cr: cursor holding lock on the cron job row, to use to
            update the next exec date,
            must not be committed/rolled back!
        """
        _intervalTypes = {
            'work_days': lambda interval: relativedelta(days=interval),
            'days': lambda interval: relativedelta(days=interval),
            'hours': lambda interval: relativedelta(hours=interval),
            'weeks': lambda interval: relativedelta(days=7*interval),
            'months': lambda interval: relativedelta(months=interval),
            'minutes': lambda interval: relativedelta(minutes=interval),
        }
        try:
            with api.Environment.manage():
                cron = api.Environment(job_cr, job['user_id'], {})[cls._name]
                # Use the user's timezone to compare and compute datetimes,
                # otherwise unexpected results may appear. For instance, adding
                # 1 month in UTC to July 1st at midnight in GMT+2 gives July 30
                # instead of August 1st!
                now = fields.Datetime.context_timestamp(cron, datetime.now())
                nextcall = fields.Datetime.context_timestamp(
                    cron, fields.Datetime.from_string(job['nextcall']))
                numbercall = job['numbercall']
                ok = False
                excluded_day = False
                if (job['excluded_days']):
                    days_to_exclude = [
                        int(x) for x in job['excluded_days'].split(',')]
                    today = now.day
                    excluded_day = today in days_to_exclude
                while nextcall < now and numbercall:
                    if numbercall > 0:
                        numbercall -= 1
                    if not excluded_day and (not ok or job['doall']):
                        cron._callback(
                            job['model'], job['function'], job['args'],
                            job['id'])
                    if numbercall:
                        nextcall += _intervalTypes[
                            job['interval_type']](job['interval_number'])
                    ok = True
                addsql = ''
                if not numbercall:
                    addsql = ', active=False'
                cron_cr.execute(
                    "UPDATE ir_cron SET nextcall=%s, numbercall=%s" +
                    addsql+" WHERE id=%s",
                    (fields.Datetime.to_string(
                        nextcall.astimezone(pytz.UTC)), numbercall, job['id']))
                cron.invalidate_cache()
        finally:
            job_cr.commit()
            cron_cr.commit()
