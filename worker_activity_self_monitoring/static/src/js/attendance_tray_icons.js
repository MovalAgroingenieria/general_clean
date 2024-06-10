odoo.define('worker_activity_self_monitoring.TrayIcon', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var TrayIcon = Widget.extend({
        template: 'tray_icon',
        events: {
            'click .o_AttendanceMenu_toggler': 'navigateToAttendance',
        },
        start: function () {
            this._super.apply(this, arguments);
            this.updateIcon();
            core.bus.on('attendance_gauge_check_in', this, this.onCheckIn);
            core.bus.on('attendance_gauge_check_out', this, this.onCheckOut);
            this.insertIcon();
        },
        insertIcon: function () {
            $(".o_menu_systray .o_tray_icon_li").remove();
            var $systray = $(".o_menu_systray");
            if ($systray.length) {
                var $li = $("<li>", { class: "o_tray_icon_li" });
                $li.append(this.$el);
                $systray.prepend($li);
            }
        },
        onCheckIn: function () {
            this.updateIcon();
            this.scheduleUpdate();
        },
        onCheckOut: function () {
            this.updateIcon();
            this.clearTimers();
        },
        updateIcon: function () {
            var self = this;
            rpc.query({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', session.uid]], ['id', 'attendance_state', 'hours_today']],
                limit: 1,
            }).then(function (employees) {
                if (employees.length > 0) {
                    var employee = employees[0];
                    self.attendanceState = employee.attendance_state;
                    self.hoursToday = employee.hours_today || 0;
                    self.lastUpdateTime = new Date();

                    self.updateAttendanceStatusIcon();

                    if (self.attendanceState === 'checked_in') {
                        self.scheduleUpdate();
                    } else {
                        self.clearTimers();
                    }
                }
            }).catch(function (error) {
                self.clearTimers();
            });
        },
        scheduleUpdate: function () {
            var self = this;

            this.clearTimers();

            var totalSecondsWorked = Math.floor(self.hoursToday * 3600);
            var residual_seconds = totalSecondsWorked % 60;
            var millisecondsUntilNextMinute = (60 - residual_seconds) * 1000;

            this.syncTimeout = setTimeout(function () {
                self.updateInterval = setInterval(self.updateDisplayedTime.bind(self), 60000);
                self.updateDisplayedTime();
            }, millisecondsUntilNextMinute);
        },
        clearTimers: function () {
            clearTimeout(this.syncTimeout);
            clearInterval(this.updateInterval);
        },
        updateAttendanceStatusIcon: function () {
            var $icon = this.$('#attendance_status_icon');
            var $hoursDisplay = this.$('#attendance_hours_display');

            $icon.removeClass('gray_circle green_circle red_circle');

            if (this.attendanceState === 'checked_in') {
                $icon.addClass('green_circle');
            } else {
                $icon.addClass('red_circle');
            }
            this.updateDisplayedTime();
        },
        updateDisplayedTime: function () {
            var now = new Date();
            var currentHours = this.hoursToday;
            if (this.attendanceState === 'checked_in') {
                var secondsSinceLastUpdate = Math.floor((now - this.lastUpdateTime) / 1000);
                var additionalMinutes = secondsSinceLastUpdate / 60;
                currentHours += additionalMinutes / 60;
            }
            var totalSecondsWorked = Math.floor(currentHours * 3600);
            var hours = Math.floor(totalSecondsWorked / 3600);
            var minutes = Math.floor((totalSecondsWorked % 3600) / 60);

            var formattedHours = [hours, minutes]
                .map(unit => String(unit).padStart(2, '0'))
                .join(':');

            this.$('#attendance_hours_display').text(formattedHours);
            console.log(`Updated displayed time: ${formattedHours}`);
        },
        navigateToAttendance: function (event) {
            event.preventDefault();
        },
        destroy: function () {
            this.clearTimers();
            this._super.apply(this, arguments);
        }
    });

    core.bus.on('web_client_ready', null, function () {
        var trayIcon = new TrayIcon();
        trayIcon.appendTo($('body'));
    });

    return TrayIcon;
});
