odoo.define('worker_activity_self_monitoring.AttendanceGaugeExtended', function (require) {
    "use strict";

    var GreetingMessage = require('hr_attendance.greeting_message');
    var core = require('web.core');

    var GreetingMessageExtended = GreetingMessage.include({
        start: function () {
            this._super.apply(this, arguments);
            console.log('GreetingMessageExtended started');
            if (this.attendance) {
                if (this.attendance.check_out) {
                    console.log('Check-out detected - triggering local event');
                    core.bus.trigger('attendance_gauge_check_out');
                } else if (this.attendance.check_in) {
                    console.log('Check-in detected - triggering local event');
                    core.bus.trigger('attendance_gauge_check_in');
                }
            }
        },
    });

    return GreetingMessageExtended;
});
