# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class WizardPreviewNotification(models.TransientModel):
    _name = 'wizard.preview.notification'
    _description = 'Dialog box to show the preview of a notification'

    notification_preview = fields.Html(
        string='Notification Preview')

    @api.model
    def default_get(self, var_fields):
        notification_preview = ''
        active_model = self.env.context.get('current_model', False)
        active_register_id = self.env.context['active_id']
        if (active_model and active_register_id):
            active_register = self.env[active_model].browse(active_register_id)
            notification_preview = active_register.rendered_main_page
            if active_register.rendered_final_paragraph:
                notification_preview = notification_preview + \
                    '<br><br><center>* * *</center><br><br>' + \
                    active_register.rendered_final_paragraph
        return {
            'notification_preview': notification_preview,
            }
