# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree
from odoo import models, fields, api, exceptions, _


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(HrAttendance, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            domain = False
            group_manager_id = self.env.ref(
                'hr_attendance.group_hr_attendance_manager').id
            group_officer_id = self.env.ref(
                'hr_attendance.group_hr_attendance_user').id
            group_staff_manager_id = self.env.ref(
                'hr_attendance_staff_manager.'
                'group_hr_attendance_staff_manager').id
            user = self.env.user
            user_groups_ids = user.groups_id.ids
            if (group_staff_manager_id in user_groups_ids and
                group_manager_id not in user_groups_ids and
                    group_officer_id not in user_groups_ids):
                employee_child_ids = user.employee_ids[0].child_ids.ids
                employee_child_ids.append(user.employee_ids[0].id)
                domain = str("[('id', 'in', %s)]") % employee_child_ids
            if domain:
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='employee_id']"):
                    node.set('domain', domain)
                res['arch'] = etree.tostring(doc)
        return res
