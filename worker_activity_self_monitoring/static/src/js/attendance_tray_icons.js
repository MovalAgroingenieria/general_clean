odoo.define('worker_activity_self_monitoring.TrayIcon', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var session = require('web.session');

    console.log('Starting TrayIcon module');

    var TrayIcon = Widget.extend({
        template: 'tray_icon',
        events: {
            'click .o_AttendanceMenu_toggler': 'navigateToAttendance',
        },
        start: function () {
            this._super.apply(this, arguments);
            console.log('TrayIcon Widget started');
            this.updateIcon();

            // Suscribirse a eventos específicos de hr_attendance
            core.bus.on('attendance_gauge_check_in', this, this.onCheckIn);
            core.bus.on('attendance_gauge_check_out', this, this.onCheckOut);

            // Insertar el icono en el lugar adecuado del DOM
            this.insertIcon();

            // Obtener la URL dinámica para la vista de asistencias
            this.setDynamicAttendanceURL();
        },
        insertIcon: function () {
            // Evitar duplicados removiendo cualquier instancia existente
            $(".o_menu_systray .o_tray_icon_li").remove();

            // Busca el contenedor de la bandeja del sistema
            var $systray = $(".o_menu_systray");
            if ($systray.length) {
                // Crea un nuevo elemento <li> y añade el contenido del widget
                var $li = $("<li>", { class: "o_tray_icon_li" });
                $li.append(this.$el);
                $systray.prepend($li); // Inserta el nuevo <li> al principio de la lista
            }
        },
        setDynamicAttendanceURL: function () {
            var self = this;

            rpc.query({
                model: 'ir.ui.menu',
                method: 'search_read',
                args: [[['name', '=', 'Asistencias']], ['id']],
                limit: 1,
            }).then(function (menus) {
                if (menus.length > 0) {
                    var menu_id = menus[0].id;
                    return rpc.query({
                        model: 'ir.actions.client',
                        method: 'search_read',
                        args: [[['tag', '=', 'hr_attendance_my_attendances']], ['id']],
                        limit: 1,
                    }).then(function (actions) {
                        if (actions.length > 0) {
                            var action_id = actions[0].id;
                            var url = `/web#menu_id=${menu_id}&action=${action_id}`;
                            self.$('.o_AttendanceMenu_toggler').attr('href', url);
                            console.log('Dynamic URL set for attendance:', url);
                        } else {
                            console.error('Action not found for attendance');
                        }
                    });
                } else {
                    console.error('Menu not found for attendance');
                }
            }).catch(function (error) {
                console.error('Error fetching dynamic URL for attendance:', error);
            });
        },
        onCheckIn: function () {
            console.log('Check-in detected');
            this.updateIcon();
            this.scheduleUpdate();
        },
        onCheckOut: function () {
            console.log('Check-out detected');
            this.updateIcon();
            this.clearTimers(); // Detiene la actualización periódica
        },
        updateIcon: function () {
            var self = this;
            console.log('Fetching data to update icon...');
            rpc.query({
                model: 'hr.employee',
                method: 'search_read',
                args: [[['user_id', '=', session.uid]], ['id', 'attendance_state', 'hours_today']],
                limit: 1,
            }).then(function (employees) {
                console.log('Employee data fetched:', employees);
                if (employees.length > 0) {
                    var employee = employees[0];
                    self.attendanceState = employee.attendance_state;
                    self.hoursToday = employee.hours_today || 0; // Horas trabajadas hasta ahora en formato decimal
                    self.lastUpdateTime = new Date(); // Hora exacta de la última actualización

                    self.updateAttendanceStatusIcon();

                    if (self.attendanceState === 'checked_in') {
                        self.scheduleUpdate();
                    } else {
                        self.clearTimers(); // Detener la actualización si no está `checked_in`
                    }
                }
            }).catch(function (error) {
                console.error('Error fetching employee data:', error);
                self.clearTimers();
            });
        },
        scheduleUpdate: function () {
            var self = this;

            // Detener cualquier temporizador existente
            this.clearTimers();

            // Calcular los segundos residuales para sincronizar con el minuto completo
            var totalSecondsWorked = Math.floor(self.hoursToday * 3600);
            var residual_seconds = totalSecondsWorked % 60;
            var millisecondsUntilNextMinute = (60 - residual_seconds) * 1000;

            console.log(`Residual seconds: ${residual_seconds}, waiting ${millisecondsUntilNextMinute} milliseconds for synchronization.`);

            // Configurar `setTimeout` para esperar hasta el próximo minuto completo solo si está `checked_in`
            this.syncTimeout = setTimeout(function () {
                console.log('Synchronizing with the next complete minute.');
                // Luego de sincronizarse con el siguiente minuto completo, actualiza cada minuto
                self.updateInterval = setInterval(self.updateDisplayedTime.bind(self), 60000);
                // Actualiza inmediatamente después de sincronizarse con el siguiente minuto completo
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

            // Actualiza la visualización de horas basada en el último tiempo exacto
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
            var totalSecondsWorked = Math.floor(currentHours * 3600); // Total de segundos trabajados hasta ahora
            var hours = Math.floor(totalSecondsWorked / 3600);
            var minutes = Math.floor((totalSecondsWorked % 3600) / 60);

            var formattedHours = [hours, minutes]
                .map(unit => String(unit).padStart(2, '0'))
                .join(':');

            this.$('#attendance_hours_display').text(formattedHours);
            console.log(`Updated displayed time: ${formattedHours}`);
        },
        navigateToAttendance: function (event) {
            // Prevenir la navegación predeterminada
            event.preventDefault();
            // No hacer nada aquí ya que el enlace <a> se encarga de la navegación
        },
        destroy: function () {
            this.clearTimers(); // Detener el intervalo al destruir el widget
            this._super.apply(this, arguments);
        }
    });

    core.bus.on('web_client_ready', null, function () {
        // Añadir el icono al cargar la página
        var trayIcon = new TrayIcon();
        trayIcon.appendTo($('body'));
    });

    return TrayIcon;
});
