odoo.define('worker_activity_self_monitoring.TaskIcon', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    console.log('Starting TaskIcon module');

    var TaskIcon = Widget.extend({
        template: 'task_icon',
        events: {
            'click .o_TaskMenu_toggler': 'navigateToTask',
        },
        start: function () {
            this._super.apply(this, arguments);
            console.log('TaskIcon Widget started');
            this.updateIcon();

            // Insertar el icono en el lugar adecuado del DOM
            this.insertIcon();
        },
        insertIcon: function () {
            // Evitar duplicados removiendo cualquier instancia existente
            $(".o_menu_systray .o_task_icon_li").remove();

            // Busca el contenedor de la bandeja del sistema
            var $systray = $(".o_menu_systray");
            if ($systray.length) {
                // Crea un nuevo elemento <li> y añade el contenido del widget
                var $li = $("<li>", { class: "o_task_icon_li" });
                $li.append(this.$el);
                $systray.prepend($li); // Inserta el nuevo <li> al principio de la lista
            }
        },
        updateIcon: function () {
            var self = this;
            console.log('Fetching data to update icon...');
            rpc.query({
                model: 'project.task',
                method: 'search_read',
                args: [
                    [
                        ['starter_user_id', '=', session.uid],  // Filtra por usuario actual
                        ['task_running', '!=', false],    // Tareas con hora de inicio
                    ],
                    ['id', 'name', 'start_time']        // Campos necesarios
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

                    // Actualiza el href a la tarea activa
                    self.$('.o_TaskMenu_toggler').attr('href', `/web#id=${self.taskId}&model=project.task&view_type=form`);
                } else {
                    self.setNoTask();
                }
            }).catch(function (error) {
                console.error('Error fetching task data:', error);
                self.setNoTask();
            });
        },
        convertToUserTimezone: function (serverDate) {
            // Convertir fecha del servidor a la zona horaria del usuario
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

            // Actualiza el href a la vista de todas las tareas con el contexto
            this.$('.o_TaskMenu_toggler').attr('href', `/web#action=project.action_view_all_task&cids=&menu_id=PROJECT_MENU_ID&search_default_my_tasks=1&all_task=0&search_default_project_tasks=1`);
        },
        navigateToTask: function (event) {
            event.preventDefault(); // Prevenir la navegación predeterminada
            // No hacemos nada aquí, ya que el href se ha configurado en `updateIcon`
        }
    });

    core.bus.on('web_client_ready', null, function () {
        // Añadir el icono al cargar la página
        var taskIcon = new TaskIcon();
        taskIcon.appendTo($('body'));
    });

    return TaskIcon;
});
