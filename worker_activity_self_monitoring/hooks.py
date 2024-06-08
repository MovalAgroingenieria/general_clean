from odoo import api, SUPERUSER_ID


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Eliminar acciones del servidor
    server_actions = env['ir.actions.server'].search([
        ('model_id.model', '=', 'worker_activity_self_monitoring.tray_icon')
    ])
    if server_actions:
        server_actions.unlink()

    # Eliminar vistas personalizadas del módulo
    views = env['ir.ui.view'].search([
        ('key', 'like', 'worker_activity_self_monitoring.%')
    ])
    if views:
        views.unlink()

    # Eliminar parámetros de configuración
    config_params = env['ir.config_parameter'].search([
        ('key', 'like', 'worker_activity_self_monitoring.%')
    ])
    if config_params:
        config_params.unlink()

    # Eliminar datos de `ir.model.data`
    model_data = env['ir.model.data'].search([
        ('module', '=', 'worker_activity_self_monitoring')
    ])
    if model_data:
        model_data.unlink()

    # Eliminar tareas programadas relacionadas
    crons = env['ir.cron'].search([
        ('name', 'like', 'worker_activity_self_monitoring.%')
    ])
    if crons:
        crons.unlink()

    # Mensaje de consola para confirmar la limpieza
    print("Worker Activity Self Monitoring module uninstalled successfully.")
