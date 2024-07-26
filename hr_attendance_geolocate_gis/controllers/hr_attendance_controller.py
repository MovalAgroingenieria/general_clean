from odoo import http
from odoo.http import request
import json
from datetime import datetime


class HrAttendanceController(http.Controller):

    @http.route("/attendances_from_dates", auth='user', type='json', methods=['POST'])
    def get_attendances_from_dates(self, **values):
        start_date = values.get('start_date')
        end_date = values.get('end_date')
        if not start_date or not end_date:
            return json.dumps({'error': 'start_date and end_date are required'})
        try:
            start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return json.dumps({'error': 'Invalid date format. Use YYYY-MM-DD'})
        domain = [
            ('check_in', '>=', start_date_dt),
            ('check_out', '<=', end_date_dt)
        ]
        attendances = request.env['hr.attendance'].search(domain)
        output = []
        for attendance in attendances:
            output.append({
                'employee_id': attendance.employee_id.id,
                'employee_name': attendance.employee_id.name,
                'check_in': attendance.check_in,
                'check_out': attendance.check_out,
                'geo_lat': attendance.geo_lat,
                'geo_long': attendance.geo_long,
                'geo_lat_out': attendance.geo_lat_out,
                'geo_long_out': attendance.geo_long_out,
            })
        return json.dumps(output)
