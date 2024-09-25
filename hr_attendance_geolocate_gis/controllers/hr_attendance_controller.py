# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http, fields
from odoo.http import request
import json
from datetime import datetime


class HrAttendanceController(http.Controller):

    @http.route("/attendances_from_dates", auth='user', type='json',
                methods=['POST'], csrf=False)
    def get_attendances_from_dates(self, *args, **kwargs):
        jsonrequest = request.jsonrequest
        start_date = jsonrequest.get('start_date')
        end_date = jsonrequest.get('end_date')
        if not start_date or not end_date:
            return json.dumps(
                {'error': 'start_date and end_date are required'})
        try:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return json.dumps({'error': 'Invalid date format. Use YYYY-MM-DD'})
        start_date_str = start_date_dt.strftime('%Y-%m-%d 00:00:00')
        end_date_str = end_date_dt.strftime('%Y-%m-%d 23:59:59')
        domain = [
            ('check_in', '>=', start_date_str),
            ('check_out', '<=', end_date_str),
        ]
        attendances = request.env['hr.attendance'].search(domain)
        output = {}
        for attendance in attendances:
            employee_name = attendance.employee_id.name
            if employee_name not in output:
                output[employee_name] = []
            output[employee_name].append({
                # Set as epoch time in milliseconds
                'check_in': (
                    fields.Datetime.from_string(attendance.check_in) -
                    datetime(1970, 1, 1)).total_seconds() * 1000,
                'check_out': (
                    fields.Datetime.from_string(attendance.check_out) -
                    datetime(1970, 1, 1)).total_seconds() * 1000,
                # If coordinates 0.0, then False to avoid weird markers
                'geo_lat': float(attendance.geo_lat) or False,
                'geo_long': float(attendance.geo_long) or False,
                'geo_lat_out': float(attendance.geo_lat_out) or False,
                'geo_long_out': float(attendance.geo_long_out) or False,
            })
        return json.dumps(output)
