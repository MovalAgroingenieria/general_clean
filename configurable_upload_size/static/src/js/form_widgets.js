odoo.define('configurable_upload_size.form_widgets', function (require) {
    "use strict";
    var core = require('web.core');
    var form_widgets = require('web.form_widgets');
    var Model = require('web.DataModel');
    var _t = core._t;
    var FieldBinaryFile = core.form_widget_registry.get('binary');
    var ConfigParameter = new Model('ir.config_parameter');
    FieldBinaryFile.include({
        init: function() {
            this._super.apply(this, arguments);
            this.max_upload_size = 25 * 1024 * 1024; // Default 25MB
            this._loadUploadSizeConfig();
        },

        _loadUploadSizeConfig: function() {
            var self = this;
            ConfigParameter.call('get_param', ['web.max_file_upload_size', '25'])
                .then(function(result) {
                    if (result) {
                        var parsed = parseInt(result);
                        if (!isNaN(parsed) && parsed > 0) {
                            self.max_upload_size = parsed * 1024 * 1024;
                        }
                    }
                });
        },

        on_file_change: function(e) {
            var self = this;
            var file = e.target.files[0];
            if (file && file.size > this.max_upload_size) {
                this.do_warn(
                    _t('File too large'),
                    _t('The selected file exceeds the maximum upload size of ') + 
                    Math.round(this.max_upload_size / (1024 * 1024)) + ' MB.'
                );
                e.target.value = '';
                return false;
            }
            return this._super.apply(this, arguments);
        }
    });
    return {
        FieldBinaryFile: form_widgets.FieldBinaryFile
    };
});
