odoo.define('worker_activity_self_monitoring.TaskIcon', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    var TaskIcon = Widget.extend({
        template: 'task_icon',
        events: {
            'click .o_TaskMenu_toggler': 'navigateToTask',
        },
        start: function () {
            this._super.apply(this, arguments);
            this.insertIcon();
            this.updateIcon();
        },
        insertIcon: function () {
            $(".o_menu_systray .o_task_icon_li").remove();

            var $systray = $(".o_menu_systray");
            if ($systray.length) {
                var $li = $("<li>", { class: "o_task_icon_li" });
                $li.append(this.$el);
                $systray.prepend($li);
            }
        },
        updateIcon: function () {
            var self = this;
            rpc.query({
                model: 'project.task',
                method: 'search_read',
                args: [
                    [
                        ['starter_user_id', '=', session.uid],
                        ['task_running', '!=', false],
                    ],
                    ['id', 'name', 'start_time']
                ],
                limit: 1,
                order: 'start_time desc'
            }).then(function (tasks) {
                console.log('Task data fetched:', tasks);
                if (tasks.length > 0) {
                    var task = tasks[0];
                    self.taskId = task.id;
                    self.taskName = task.name;
                    self.taskStartTime = self.convertToUserTimezone(task.start_time);
                    self.updateTaskStatusIcon();
                    $('.o_TaskMenu_toggler').attr('href', `/web#id=${self.taskId}&model=project.task&view_type=form&action=project.action_view_all_task`);
                } else {
                    self.setNoTask();
                }
            }).catch(function (error) {
                self.setNoTask();
            });
        },
        convertToUserTimezone: function (serverDate) {
            return moment.utc(serverDate).local().toDate();
        },
        updateTaskStatusIcon: function () {
            var $icon = this.$('#task_status_icon');
            var $taskDisplay = this.$('#task_name_display');
            $icon.removeClass('gray_circle green_circle');
            if (this.taskId) {
                $icon.addClass('green_circle');
                var taskName = this.taskName.length > 30 ? this.taskName.substring(0, 30).trim() + '...' : this.taskName;
                $taskDisplay.text(taskName).show();
            } else {
                $icon.addClass('gray_circle');
                $taskDisplay.hide();
            }
        },
        setNoTask: function () {
            var $icon = this.$('#task_status_icon');
            var $taskDisplay = this.$('#task_name_display');
            this.taskId = null;
            this.taskName = '';
            this.taskStartTime = null;
            $icon.removeClass('gray_circle green_circle').addClass('gray_circle');
            $taskDisplay.hide();
            $('.o_TaskMenu_toggler').attr('href', `/web#action=project.action_view_all_task`);
        },
        navigateToTask: function (event) {
            event.preventDefault();
        }
    });

    core.bus.on('web_client_ready', null, function () {
        var taskIcon = new TaskIcon();
        taskIcon.appendTo($('body'));
    });

    return TaskIcon;
});
