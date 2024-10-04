# -*- coding: utf-8 -*-
# Copyright 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request
from odoo.addons.eom_authdnie.controllers.main import WebsiteEom


class WebsiteEOffice(WebsiteEom):

    @http.route('/efiles', type='http', auth='public', website=True,
                csrf=False)
    def get_electronic_files(self, **kwargs):
        country = ''
        dni = ''
        firstname = ''
        lastname = ''
        authority = ''
        identif_token = ''
        model_digitalregister = request.env['eom.digitalregister'].sudo()
        if request.httprequest.method == 'POST':
            identif_token = kwargs.get('identif_token', False)
            if identif_token:
                plain_text = model_digitalregister.decrypt_data(identif_token)
                if plain_text:
                    country, dni, firstname, lastname, authority = \
                        model_digitalregister.get_items_of_decrypted_identif(
                            plain_text)
        if country and dni and firstname and lastname and authority:
            dni = country + dni
            digitalregister = model_digitalregister.search(
                [('name', '=', dni)])
            if digitalregister and len(digitalregister) == 1:
                digitalregister = digitalregister[0]
            else:
                digitalregister = False
            return request.render(
                'eom_eoffice.electronic_files_page',
                {'identif_token': identif_token,
                 'identif_header': (lastname + ', ' + firstname +
                                    ' (' + dni + ')'),
                 'digitalregister': digitalregister, })
        else:
            return request.render(
                'eom_authdnie.identification_error', {})

    @http.route('/getdocument', type='http', auth='public', website=True,
                csrf=False)
    def get_document_from_csv(self, **kwargs):
        country = ''
        dni = ''
        firstname = ''
        lastname = ''
        authority = ''
        identif_token = ''
        model_digitalregister = request.env['eom.digitalregister'].sudo()
        if request.httprequest.method == 'POST':
            identif_token = kwargs.get('identif_token', False)
            if identif_token:
                plain_text = model_digitalregister.decrypt_data(identif_token)
                if plain_text:
                    country, dni, firstname, lastname, authority = \
                        model_digitalregister.get_items_of_decrypted_identif(
                            plain_text)
        if country and dni and firstname and lastname and authority:
            dni = country + dni
            digitalregister = model_digitalregister.search(
                [('name', '=', dni)])
            if digitalregister and len(digitalregister) == 1:
                digitalregister = digitalregister[0]
            else:
                digitalregister = False
            return request.render(
                'eom_eoffice.csv_code_form',
                {'identif_token': identif_token,
                 'identif_header': (lastname + ', ' + firstname +
                                    ' (' + dni + ')'),
                 'digitalregister': digitalregister, })
        else:
            return request.render(
                'eom_authdnie.identification_error', {})

    @http.route('/genericinstance', type='http', auth='public', website=True,
                csrf=False)
    def create_generic_instance(self, **kwargs):
        country = ''
        dni = ''
        firstname = ''
        lastname = ''
        authority = ''
        identif_token = ''
        model_digitalregister = request.env['eom.digitalregister'].sudo()
        if request.httprequest.method == 'POST':
            identif_token = kwargs.get('identif_token', False)
            if identif_token:
                plain_text = model_digitalregister.decrypt_data(identif_token)
                if plain_text:
                    country, dni, firstname, lastname, authority = \
                        model_digitalregister.get_items_of_decrypted_identif(
                            plain_text)
        if country and dni and firstname and lastname and authority:
            dni = country + dni
            digitalregister = model_digitalregister.search(
                [('name', '=', dni)])
            if digitalregister and len(digitalregister) == 1:
                digitalregister = digitalregister[0]
            else:
                digitalregister = False
            return request.render(
                'eom_eoffice.generic_instance_form',
                {'identif_token': identif_token,
                 'identif_header': (lastname + ', ' + firstname +
                                    ' (' + dni + ')'),
                 'digitalregister': digitalregister, })
        else:
            return request.render(
                'eom_authdnie.identification_error', {})

    @http.route('/suggestion', type='http', auth='public', website=True,
                csrf=False)
    def create_suggestion(self, **kwargs):
        country = ''
        dni = ''
        firstname = ''
        lastname = ''
        authority = ''
        identif_token = ''
        model_digitalregister = request.env['eom.digitalregister'].sudo()
        if request.httprequest.method == 'POST':
            identif_token = kwargs.get('identif_token', False)
            if identif_token:
                plain_text = model_digitalregister.decrypt_data(identif_token)
                if plain_text:
                    country, dni, firstname, lastname, authority = \
                        model_digitalregister.get_items_of_decrypted_identif(
                            plain_text)
        if country and dni and firstname and lastname and authority:
            dni = country + dni
            digitalregister = model_digitalregister.search(
                [('name', '=', dni)])
            if digitalregister and len(digitalregister) == 1:
                digitalregister = digitalregister[0]
            else:
                digitalregister = False
            return request.render(
                'eom_eoffice.suggestion_form',
                {'identif_token': identif_token,
                 'identif_header': (lastname + ', ' + firstname +
                                    ' (' + dni + ')'),
                 'digitalregister': digitalregister, })
        else:
            return request.render(
                'eom_authdnie.identification_error', {})

    @http.route('/confirmation', type='http', auth='public', website=True,
                csrf=False)
    def confirm_procedure(self, **kwargs):
        country = ''
        dni = ''
        firstname = ''
        lastname = ''
        authority = ''
        identif_token = ''
        model_digitalregister = request.env['eom.digitalregister'].sudo()
        if request.httprequest.method == 'POST':
            identif_token = kwargs.get('identif_token', False)
            if identif_token:
                plain_text = model_digitalregister.decrypt_data(identif_token)
                if plain_text:
                    country, dni, firstname, lastname, authority = \
                        model_digitalregister.get_items_of_decrypted_identif(
                            plain_text)
        if country and dni and firstname and lastname and authority:
            dni = country + dni
            digitalregister = model_digitalregister.search(
                [('name', '=', dni)])
            electronicfile_code = ''
            if digitalregister and len(digitalregister) == 1:
                digitalregister = digitalregister[0]
                electronicfile_type = kwargs.get('electronicfile_type', False)
                if electronicfile_type:
                    vals = {'digitalregister_id': digitalregister.id,
                            'type': electronicfile_type, }
                    if electronicfile_type == '01_generic_instance':
                        vals['exposition'] = kwargs.get('exposition', False)
                        vals['request'] = kwargs.get('request', False)
                    elif electronicfile_type == '02_suggestion':
                        vals['suggestion'] = kwargs.get('suggestion', False)
                    # TODO (other "if")
                    model_electronicfile = request.env['eom.electronicfile'].sudo()
                    electronicfile = model_electronicfile.create(vals)
                    electronicfile_code = electronicfile.name
                    uploaded_files = request.httprequest.files.getlist(
                        'attachments')
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            name = uploaded_file.filename
                            datas = uploaded_file.read().encode('base64')
                            if name and datas:
                                model_ir_attachment = \
                                    request.env['ir.attachment'].sudo()
                                model_ir_attachment.create({
                                    'name': name,
                                    'datas': datas,
                                    'datas_fname': name,
                                    'type': 'binary',
                                    'res_name': electronicfile.name,
                                    'res_model': 'eom.electronicfile',
                                    'res_id': electronicfile.id, })
                else:
                    digitalregister = False
            else:
                digitalregister = False
            return request.render(
                'eom_eoffice.confirmation_and_home',
                {'identif_token': identif_token,
                 'identif_header': (lastname + ', ' + firstname +
                                    ' (' + dni + ')'),
                 'digitalregister': digitalregister,
                 'electronicfile_code': electronicfile_code, })
        else:
            return request.render(
                'eom_authdnie.identification_error', {})
