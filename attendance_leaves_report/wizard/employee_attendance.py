# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from odoo import models, fields, api


class EmployeeAttendance(models.Model):
    _name = 'employee.attendance.wizard'

    def _default_employee_ids(self):
        context = self._context
        active_ids = context.get('active_ids')
        employees = self.env['hr.employee'].search([('id', 'in', active_ids)])
        return employees

    def _default_number_of_selected_employees(self):
        context = self._context
        active_ids = context.get('active_ids')
        return len(active_ids)

    report_date = fields.Datetime(
        string='Report date',
        store=True,
        default=datetime.datetime.now(),
        compute="_compute_report_date")

    start_date = fields.Datetime(
        string='Start date',
        required=True)

    end_date = fields.Datetime(
        string='End date',
        required=True)

    employee_ids = fields.Many2many(
        string="Employees",
        store=True,
        comodel_name="hr.employee",
        default=_default_employee_ids,
        compute="_compute_employee_ids")

    number_of_selected_employees = fields.Integer(
        string="Num. selected employees",
        readonly=True,
        default=_default_number_of_selected_employees)

    @api.multi
    def _compute_report_date(self):
        for record in self:
            record.report_date = datetime.datetime.now()

    @api.multi
    def _compute_employee_ids(self):
        active_ids = employees = False
        context = self._context
        active_ids = context.get('active_ids')
        if active_ids:
            employees = self.env['hr.employee'].search(
                [('id', 'in', active_ids)])
        if employees:
            self.employee_ids = employees

    @api.multi
    def print_employee_attendance_report(self):
        self.ensure_one()
        data = {
            'model': 'hr.attendance',
            'start_date': self.start_date,
            'end_date': self.end_date,
            'employee_ids': self.employee_ids.ids}
        return self.env['report'].get_action(
            self, 'attendance_leaves_report.template_employee_attendance')
