odoo.define('law_water_quality_remotecontrol.button_import_measurements', function (require) {
"use strict";

var ListView = require('web.ListView');
var Model = require('web.DataModel');
var core = require('web.core');


ListView.include({
    // Get Context of the action
    init: function (parent, action) {
        this.odoo_context = action.context;
        return this._super.apply(this, arguments);
    },
    render_buttons: function() {
        this._super.apply(this, arguments);
        if (this.$buttons) {
            // Check if comes from other model shortcut  and in that case
            // don't show button, because confuses (All measu)
            var fromShortcut = this.odoo_context &&
                this.odoo_context.from_shortcut;
            var btn = this.$buttons.find('.button_import_measurements');
            if (fromShortcut) {
                btn.hide();
            } else {
                btn.on('click', this.proxy('do_button_import_measurements'));
            }
        }
    },
    do_button_import_measurements: function() {
        var _t = core._t;
        var message = _t('Import measurements?')
        var confirmed = confirm(message);
        if (confirmed) {
            var python_function = new Model('law.measuring.device.measurement').
                                  call("do_import_measurements",[]);
            python_function.done(function(result) {
                var title_number_of_measurements = _t('Number of measurements');
                var title_error_message = _t('WARNING');
                var number_of_measurements = result[1];
                var error_message = result[2];
                var result_message = title_number_of_measurements + ': ' +
                                     number_of_measurements.toString();
                if (error_message != '') {
                    result_message = result_message + '\n\n' +
                                     title_error_message + ': ' +
                                     error_message;
                }
                window.alert(result_message);
                if (number_of_measurements > 0) {
                    window.location.reload(false);
                }
            });
        }
    }
});

})