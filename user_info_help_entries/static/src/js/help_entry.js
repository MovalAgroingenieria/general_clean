odoo.define('user_info_help_entries.help_entry', function (require) {
    'use strict';

    var UserMenu = require('web.UserMenu');
    var Model = require('web.DataModel');
    var session = require('web.session');

    UserMenu.include({
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var userHelpEntryModel = new Model('user.menu.help.entry');

                // Fetch entries along with groups and order by name ascending
                return userHelpEntryModel.query(['name', 'url', 'groups'])
                    .filter([['active', '=', true]])
                    .order_by(['name'])
                    .all().then(function (entries) {
                        if (!entries || !entries.length) {
                            // No entries to process
                            return;
                        }
                        // Filter entries by user groups
                        self._filterEntriesByUserGroups(entries);
                    });
            });
        },

        _filterEntriesByUserGroups: function (entries) {
            var self = this;
            var userModel = new Model('res.users');

            // Fetch user's groups
            userModel.call('read', [[session.uid], ['groups_id']]).then(function (userData) {
                var userGroups = userData && userData[0] && userData[0].groups_id ? userData[0].groups_id : [];

                // Filter entries that match user's groups
                var filteredEntries = _.filter(entries, function (entry) {
                    // Entries with no groups are visible to everyone
                    if (!entry.groups || entry.groups.length === 0) {
                        return true;
                    }

                    // Check if user's groups intersect with entry's groups
                    return _.intersection(entry.groups, userGroups).length > 0;
                });

                // Render the filtered entries
                if (filteredEntries.length > 0) {
                    self._renderHelpEntries(filteredEntries);
                }
            });
        },

        _renderHelpEntries: function (entries) {
            var $settingsMenu = this.$el.find("a[data-menu='settings']").parent();

            _.each(entries, function (entry) {
                var url = entry.url;

                var $li = $('<li/>');
                var $a = $('<a/>', {
                    href: url,
                    target: '_blank',
                    text: entry.name,
                });
                $li.append($a);
                $settingsMenu.before($li);
            });

            // Insert the divider once before adding entries
            if (!$settingsMenu.prev('li.divider').length) {
                $settingsMenu.before($('<li name="divider" class="divider"/>'));
            }
        },
    });
});
