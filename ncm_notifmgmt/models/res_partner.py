# -*- coding: utf-8 -*-
# Copyright 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    notif_name = fields.Char(
        string='Notifications: Partner Name',
        compute='_compute_notif_name',)

    notif_address_1 = fields.Char(
        string='Notifications: Partner Address (street and number)',
        compute='_compute_notif_address_1',)

    notif_address_2 = fields.Char(
        string='Notifications: Partner Address (zip, city, state and country)',
        compute='_compute_notif_address_2',)

    notif_phone = fields.Char(
        string='Notifications: Phone',
        compute='_compute_notif_phone',)

    notif_email = fields.Char(
        string='Notifications: Email',
        compute='_compute_notif_email',)

    notif_vat = fields.Char(
        string='Notifications: VAT',
        compute='_compute_notif_vat',)

    notification_ids = fields.One2many(
        string='Notifications',
        comodel_name='res.notification',
        inverse_name='partner_id')

    number_of_notifications = fields.Integer(
        string='Number of notifications',
        compute_sudo=True,
        compute='_compute_number_of_notifications',)

    number_of_selected_notifications = fields.Integer(
        string='Number of selected notifications',
        compute_sudo=True,
        compute='_compute_number_of_selected_notifications',)

    @api.multi
    def _compute_notif_name(self):
        for record in self:
            record.notif_name = record.name

    @api.multi
    def _compute_notif_address_1(self):
        for record in self:
            notif_address_1 = ''
            if record.street and record.street2:
                notif_address_1 = record.street + ' ' + record.street2
            else:
                if record.street or record.street2:
                    if record.street:
                        notif_address_1 = record.street
                    else:
                        notif_address_1 = record.street2
            record.notif_address_1 = notif_address_1

    @api.multi
    def _compute_notif_address_2(self):
        for record in self:
            notif_address_2 = ''
            zipcode = ''
            if record.zip:
                zipcode = record.zip
            city = ''
            if record.city:
                city = record.city
            zip_and_city = (zipcode + ' ' + city).strip()
            state_and_country = ''
            state = ''
            if record.state_id:
                state = record.state_id.name
            country = ''
            if record.country_id:
                country = record.country_id.name
            if state and country:
                state_and_country = state + ', ' + country
            else:
                if state or country:
                    if state:
                        state_and_country = state
                    else:
                        state_and_country = country
            if zip_and_city and state_and_country:
                notif_address_2 = zip_and_city + ' (' + state_and_country + ')'
            else:
                if zip_and_city or state_and_country:
                    if zip_and_city:
                        notif_address_2 = zip_and_city
                    else:
                        notif_address_2 = state_and_country
            record.notif_address_2 = notif_address_2

    @api.multi
    def _compute_notif_phone(self):
        for record in self:
            record.notif_phone = record.phone

    @api.multi
    def _compute_notif_email(self):
        for record in self:
            record.notif_email = record.email

    @api.multi
    def _compute_notif_vat(self):
        for record in self:
            notif_vat = ''
            if record.vat and len(record.vat) > 2:
                notif_vat = record.vat[2:]
            record.notif_vat = notif_vat

    @api.multi
    def _compute_number_of_notifications(self):
        for record in self:
            number_of_notifications = 0
            if record.notification_ids:
                number_of_notifications = len(record.notification_ids)
            record.number_of_notifications = number_of_notifications

    @api.multi
    def _compute_number_of_selected_notifications(self):
        for record in self:
            number_of_selected_notifications = 0
            if record.notification_ids:
                for notification in record.notification_ids:
                    if (notification.selected and
                       notification.state != '01_draft'):
                        number_of_selected_notifications = \
                            number_of_selected_notifications + 1
            record.number_of_selected_notifications = \
                number_of_selected_notifications

    @api.multi
    def action_get_selected_notifications(self):
        self.ensure_one()
        current_partner = self
        id_tree_view = self.env.ref(
            'ncm_notifmgmt.res_notification_generated_particular_view_tree').id
        id_form_view = self.env.ref(
            'ncm_notifmgmt.res_notification_view_form').id
        search_view = self.env.ref(
            'ncm_notifmgmt.res_notification_generated_particular_view_search')
        act_window = {
            'type': 'ir.actions.act_window',
            'name': _('Notifications'),
            'res_model': 'res.notification',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'views': [(id_tree_view, 'tree'), (id_form_view, 'form')],
            'search_view_id': [search_view.id],
            'target': 'current',
            'domain': [('partner_id', '=', current_partner.id),
                       ('selected', '=', True),
                       ('state', '!=', '01_draft')],
            }
        return act_window
