odoo.define('web_fix_mobile_back_button.button_import_readings', function (require) {
"use strict";

var ViewManager = require('web.ViewManager');

ViewManager.include({
    create_view: function(view, view_options) {
        var self = this;
        // Check if fields view is created
        if (!view.fields_view) {
            view.fields_view = {'arch': {'attrs': {'js_class': undefined}}}
        }
        var js_class = view.fields_view.arch.attrs && view.fields_view.arch.attrs.js_class;
        var View = this.registry.get(js_class || view.type);
        var options = _.clone(view.options);
        if (view.type === "form" && ((this.action.target === 'new' || this.action.target === 'inline') ||
            (view_options && view_options.mode === 'edit'))) {
            options.initial_mode = options.initial_mode || 'edit';
        }

        var controller = new View(this, this.dataset, view.fields_view, options);

        controller.on('switch_mode', this, this.switch_mode.bind(this));
        controller.on('history_back', this, function () {
            if (self.action_manager) self.action_manager.trigger('history_back');
        });
        controller.on("change:title", this, function() {
            if (self.action_manager && !self.flags.headless) {
                var breadcrumbs = self.action_manager.get_breadcrumbs();
                self.update_control_panel({breadcrumbs: breadcrumbs}, {clear: false});
            }
        });

        return controller;
    },
});

})