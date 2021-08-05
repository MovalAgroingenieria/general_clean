# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import locale
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, models, _
from odoo.tools import pytz


class EmployeeAttendanceReport(models.Model):
    _name = 'report.attendance_leaves_report.template_employee_attendance'

    @api.multi
    def get_formatted_date(self, date):
        input_date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        user_tz_date = pytz.utc.localize(input_date).astimezone(tz)
        date_without_tz = user_tz_date.replace(tzinfo=None)
        return date_without_tz

    @api.multi
    def get_difference(self, check_in, check_out):
        check_in = self.get_formatted_date(check_in)
        check_out = self.get_formatted_date(check_out)
        difference = relativedelta(check_out, check_in)
        hours = difference.hours
        minutes = difference.minutes
        difference_time = str(hours).zfill(2) + ':' + str(minutes).zfill(2)
        return difference_time, difference

    def get_translated_weekday(self, day_num):
        translated_weekday = ""
        if day_num == 0:
            translated_weekday = _('Monday')
        if day_num == 1:
            translated_weekday = _('Tuesday')
        if day_num == 2:
            translated_weekday = _('Wednesday')
        if day_num == 3:
            translated_weekday = _('Thursday')
        if day_num == 4:
            translated_weekday = _('Friday')
        if day_num == 5:
            translated_weekday = _('Saturday')
        if day_num == 6:
            translated_weekday = _('Sunday')
        return translated_weekday

    @api.multi
    def get_attendance_data(self, o, employee_id):
        data = []
        start = self.get_formatted_date(o.start_date)
        end = self.get_formatted_date(o.end_date)
        attendance_ids = self.env['hr.attendance'].search(
            [('check_in', '>=', str(start)), ('check_out', '<=', str(end)),
             ('employee_id', '=', employee_id.id)], order='check_in')
        if attendance_ids:
            difference_time = ''
            total_working_time = relativedelta(
                days=0, hours=0, minutes=0, seconds=0)
            total_working_time_show = ''
            for attendance in attendance_ids:
                check_in = self.get_formatted_date(attendance.check_in)
                check_out = ''
                check_in_show = datetime.strptime(
                    attendance.check_in, "%Y-%m-%d %H:%M:%S").strftime(
                        "%d/%m/%Y %H:%M")
                check_in_weekday = self.get_translated_weekday(
                    datetime.strptime(attendance.check_in, "%Y-%m-%d %H:%M:%S"
                                      ).weekday())
                check_in_show = check_in_show + ' - ' + check_in_weekday
                check_out_show = ''
                if attendance.check_out:
                    check_out = \
                        self.get_formatted_date(attendance.check_out)
                    difference_time, difference = \
                        self.get_difference(check_in, check_out)
                    total_working_time += difference
                    days_in_hours = total_working_time.days * 24
                    total_hours = days_in_hours + total_working_time.hours
                    if total_hours < 10:
                        total_hours = str(total_hours).zfill(2)
                    else:
                        total_hours = str(total_hours)
                    total_working_time_show = total_hours + ':' + \
                        str(total_working_time.minutes).zfill(2)
                    check_out_show = datetime.strptime(
                        attendance.check_out, "%Y-%m-%d %H:%M:%S").strftime(
                        "%d/%m/%Y %H:%M")
                    check_out_weekday = self.get_translated_weekday(
                        datetime.strptime(attendance.check_out,
                                          "%Y-%m-%d %H:%M:%S").weekday())
                    check_out_show = check_out_show + ' - ' + check_out_weekday
                data.append(
                    {'check_in': check_in_show,
                     'check_out': check_out_show,
                     'difference': difference_time,
                     'total_working_time_show': total_working_time_show})
        return data

    @api.multi
    def get_leaves_details(self, o, employee_id):
        data = []
        start = self.get_formatted_date(o.start_date)
        end = self.get_formatted_date(o.end_date)
        results = []
        employee_leaves = self.env['hr.holidays'].search(
            [('employee_id', '=', employee_id.id), ('type', '=', 'remove'),
             ('holiday_type', '=', 'employee'), ('state', '=', 'validate')],
            order='date_from')
        for employee_leave in employee_leaves:
            from_date = self.get_formatted_date(employee_leave.date_from)
            to_date = self.get_formatted_date(employee_leave.date_to)
            if from_date >= start and from_date <= end:
                results.append(employee_leave)
            elif to_date >= start and to_date <= end:
                results.append(employee_leave)
        if results:
            for leave_id in results:
                from_date = \
                    datetime.strptime(
                        leave_id.date_from, "%Y-%m-%d %H:%M:%S").strftime(
                            "%d/%m/%Y %H:%M")
                from_date_weekday = self.get_translated_weekday(
                    datetime.strptime(leave_id.date_from, "%Y-%m-%d %H:%M:%S"
                                      ).weekday())
                from_date = from_date + ' - ' + from_date_weekday
                to_date = \
                    datetime.strptime(
                        leave_id.date_to, "%Y-%m-%d %H:%M:%S").strftime(
                            "%d/%m/%Y %H:%M")
                to_date_weekday = self.get_translated_weekday(
                    datetime.strptime(leave_id.date_from, "%Y-%m-%d %H:%M:%S"
                                      ).weekday())
                to_date = to_date + ' - ' + to_date_weekday
                total_num_of_days = self.transform_float_to_locale(
                    abs(leave_id.number_of_days), 2)
                from_date_2 = self.get_formatted_date(
                    datetime.strptime(leave_id.date_from, "%Y-%m-%d %H:%M:%S"))
                to_date_2 = self.get_formatted_date(
                    datetime.strptime(leave_id.date_to, "%Y-%m-%d %H:%M:%S"))
                if start < from_date_2 and end > to_date_2:
                    period_num_of_days = total_num_of_days
                elif start < from_date_2:
                    difference = relativedelta(from_date_2, end)
                    total_seconds = abs((difference.days * 24 * 3600) +
                        (difference.hours * 3600) + (difference.minutes * 60)
                        + difference.seconds)
                    diff_days = total_seconds / 86400.0
                    period_num_of_days = self.transform_float_to_locale(
                        diff_days, 2)
                elif end > to_date_2:
                    difference = relativedelta(start, to_date_2)
                    total_seconds = abs((difference.days * 24 * 3600) +
                        (difference.hours * 3600) + (difference.minutes * 60)
                        + difference.seconds)
                    diff_days = total_seconds / 86400.0
                    period_num_of_days = self.transform_float_to_locale(
                        diff_days, 2)
                data.append({'type': leave_id.holiday_status_id.name,
                             'from': from_date,
                             'to': to_date,
                             'reason': leave_id.name,
                             'total_num_of_days': total_num_of_days,
                             'period_num_of_days': period_num_of_days})
        return data

    @api.multi
    def get_public_holidays(self, o):
        data = []
        start = self.get_formatted_date(o.start_date)
        end = self.get_formatted_date(o.end_date)
        public_holidays = self.env['hr.holidays.public.line'].search(
            [('date', '>=', str(start)), ('date', '<=', str(end))],
            order='date')
        if public_holidays:
            for public_holiday in public_holidays:
                holiday_date = datetime.strptime(
                    public_holiday.date, "%Y-%m-%d").strftime(
                        "%d/%m/%Y")
                holiday_date_weekday = self.get_translated_weekday(
                    datetime.strptime(public_holiday.date, "%Y-%m-%d"
                                      ).weekday())
                holiday_date = holiday_date + ' - ' + holiday_date_weekday
                data.append(
                    {'holiday_date': holiday_date,
                     'holiday_name': public_holiday.name})
        return data

    @api.model
    def transform_float_to_locale(self, float_number, precision):
        precision = '%.' + str(precision) + 'f'
        locale.setlocale(locale.LC_NUMERIC,
                         str(self.env.context['lang'] + '.utf8'))
        formated_float_number = locale.format(precision, float_number, True)
        locale.resetlocale(locale.LC_NUMERIC)
        return formated_float_number

    @api.model
    def render_html(self, docids, data=None):
        docs = self.env['employee.attendance.wizard'].browse(docids)
        docargs = {'doc_ids': docids,
                   'doc_model': 'employee.attendance.wizard',
                   'docs': docs,
                   'get_attendance_data': self.get_attendance_data,
                   'get_leaves_details': self.get_leaves_details,
                   'get_public_holidays': self.get_public_holidays}
        return self.env['report'].render(
            'attendance_leaves_report.template_employee_attendance', docargs)
