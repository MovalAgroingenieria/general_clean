odoo.define('base.tray_icons', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var TrayIcon = Widget.extend({
        template: 'TrayIcon',
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.odoo_context = action.context;
        },
        start: function () {
            var self = this;
            this._super.apply(this, arguments);
            // Fetch data from the backend and render the icons
            this.updateIcons();
        },
        updateIcons: function () {
            var self = this;

            // Fetch the employee ID for the current user
            rpc.query({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', session.uid]], ['id']],
                limit: 1
            }).then(function (employees) {
                if (employees.length > 0) {
                    var employeeId = employees[0].id;
                    // Now search for active attendance for this employee
                    return rpc.query({
                        model: 'hr.attendance',
                        method: 'search_read',
                        args: [[['employee_id', '=', employeeId], ['check_out', '=', false]], ['id']],
                        limit: 1
                    });
                } else {
                    return Promise.resolve([]); // No employee found
                }
            }).then(function (attendances) {
                self.updateAttendanceStatusIcon(attendances.length > 0);
            }).catch(function (error) {
                console.error('Error in fetching data:', error);
                // Handle error and retry if necessary
                setTimeout(self.updateIcons.bind(self), 5000);
            });
        },
        updateAttendanceStatusIcon: function (hasActiveAttendance) {
            var $icon = this.$('#attendance_status_icon');
            $icon.removeClass('gray_circle green_circle red_circle');

            // Update the color based on active attendance status
            if (hasActiveAttendance) {
                $icon.addClass('green_circle');
            } else {
                $icon.addClass('red_circle');
            }
        }
    });

    core.action_registry.add('tray_icons', TrayIcon);

    return TrayIcon;
});
