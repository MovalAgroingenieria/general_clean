# -*- coding: utf-8 -*-
# Copyright 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from Crypto import Random
from Crypto.Cipher import AES
from odoo import models, fields, api


class EomDigitalregister(models.Model):
    _name = 'eom.digitalregister'
    _description = 'Digital Register'
    _order = 'name'

    SIZE_NAME = 20
    SIZE_FIRSTNAME = 50
    SIZE_LASTNAME = 50
    SIZE_AUTHORITY = 50

    # IMPORTANT: This cipher key must be replaced in the custom module (and
    # in the related PHP). Or preferably in a new custom module that is
    # outside the repository (in this way, it is outside the AGPL license and
    # does not have to be delivered.).
    _cipher_key = 'a%C*F-JaNdRgUkXqj8Ymx59IYhv0vHe2'

    name = fields.Char(
        string='DNI',
        size=SIZE_NAME,
        required=True,
        index=True,)

    firstname = fields.Char(
        string='First Name',
        size=SIZE_FIRSTNAME,
        index=True,)

    lastname = fields.Char(
        string='Last Name',
        size=SIZE_LASTNAME,
        index=True,)

    authority = fields.Char(
        string='Authority',
        size=SIZE_AUTHORITY,
        index=True,)

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        index=True,
        ondelete='restrict',)

    digitalregisteraccess_ids = fields.One2many(
        string='Accesses of the digital register',
        comodel_name='eom.digitalregister.access',
        inverse_name='digitalregister_id')

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)',
         'Existing digital register.'),
        ]

    @api.model
    def encrypt_data(self, data_to_encrypt):
        resp = ''
        cipher_key = self._cipher_key
        if data_to_encrypt and cipher_key:
            # Adaptation of cipher_key
            limit = 16
            len_cipher_key = len(cipher_key)
            if len_cipher_key > 16 and len_cipher_key <= 24:
                limit = 24
            elif len_cipher_key > 24:
                limit = 32
            if len_cipher_key < limit:
                cipher_key = cipher_key + ' ' * (limit - len_cipher_key)
            if len_cipher_key > limit:
                cipher_key = cipher_key[:limit]
            # Adaptation for 16-multiple
            block_size = AES.block_size
            data_to_encrypt = data_to_encrypt.encode('utf-8')
            len_of_data_to_encrypt = len(data_to_encrypt)
            rest = len_of_data_to_encrypt % block_size
            if rest > 0:
                data_to_encrypt = data_to_encrypt + ' ' * (block_size - rest)
            # Encrypt
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
            encrypted_data = cipher.encrypt(data_to_encrypt)
            # Coding to base64
            resp = base64.b64encode(iv + encrypted_data)
        return resp

    @api.model
    def decrypt_data(self, encrypted_data):
        resp = ''
        cipher_key = self._cipher_key
        if encrypted_data and cipher_key:
            block_size = AES.block_size
            # Decoding from base64
            try:
                encrypted_content = base64.b64decode(encrypted_data)
            except Exception:
                encrypted_content = ''
            if len(encrypted_content) > block_size:
                # Extract iv and encrypted data without iv
                iv = encrypted_content[:block_size]
                encrypted_data = encrypted_content[block_size:]
                # Adaptation of cipher_key
                limit = 16
                len_cipher_key = len(cipher_key)
                if len_cipher_key > 16 and len_cipher_key <= 24:
                    limit = 24
                elif len_cipher_key > 24:
                    limit = 32
                if len_cipher_key < limit:
                    cipher_key = cipher_key + ' ' * (limit - len_cipher_key)
                if len_cipher_key > limit:
                    cipher_key = cipher_key[:limit]
                # Decrypt
                cipher = AES.new(cipher_key, AES.MODE_CBC, iv)
                raw_decrypted_data = cipher.decrypt(encrypted_data)
                resp = raw_decrypted_data.rstrip()
        return resp

    @api.model
    def get_items_of_decrypted_identif(self, decrypted_identif):
        country = ''
        dni = ''
        firstname = ''
        lastname = ''
        authority = ''
        item_list = decrypted_identif.split(':')
        if item_list and len(item_list) >= 5:
            country = item_list[0]
            dni = item_list[1]
            firstname = item_list[3]
            lastname = item_list[2]
            authority = item_list[4]
        return country, dni, firstname, lastname, authority

    @api.model
    def create_access(self, dni, firstname, lastname, authority):
        if dni and firstname and lastname and authority:
            # First: if the record does not exist in the "eom.digitalregister"
            # model, it is mandatory to create it.
            digitalregister = self.search([('name', '=', dni)])
            if not digitalregister:
                vals = {
                    'name': dni,
                    'firstname': firstname,
                    'lastname': lastname,
                    'authority': authority,
                    }
                partner_id = None
                model_res_partner = self.env['res.partner']
                possible_partners = model_res_partner.search(
                    [('vat', '=', dni)])
                if possible_partners and len(possible_partners) == 1:
                    partner_id = possible_partners[0].id
                if partner_id:
                    vals['partner_id'] = partner_id
                digitalregister = self.create(vals)
            else:
                digitalregister = digitalregister[0]
            # Second: add the access to digital register.
            model_digitalregister_access = \
                self.env['eom.digitalregister.access']
            new_access = model_digitalregister_access.create({
                'digitalregister_id': digitalregister.id, })
            # digitalregister.write({
            #     'digitalregisteraccess_ids': [(0, 0, {})]
            #     })
            return new_access
        else:
            return False


class EomDigitalregisterAccess(models.Model):
    _name = 'eom.digitalregister.access'
    _description = 'Access of a digital register'
    _order = 'name'

    SIZE_NAME = 50
    SIZE_SUMMARY = 75
    SIZE_DETAIL = 255

    event_time = fields.Datetime(
        string='Time',
        default=lambda self: fields.datetime.now(),
        required=True,
        index=True,
        readonly=True,)

    digitalregister_id = fields.Many2one(
        string='Digital Register',
        comodel_name='eom.digitalregister',
        required=True,
        index=True,
        readonly=True,
        ondelete='cascade',)

    name = fields.Char(
        size=SIZE_NAME,
        store=True,
        index=True,
        compute='_compute_name',)

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        store=True,
        index=True,
        compute='_compute_partner_id',
        ondelete='restrict',)

    summary = fields.Char(
        string='Summary',
        size=SIZE_SUMMARY,
        required=True,
        index=True,)

    detail = fields.Char(
        string='Detail',
        size=SIZE_DETAIL,)

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)',
         'Existing access.'),
        ]

    @api.depends('event_time', 'digitalregister_id')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.event_time and record.digitalregister_id:
                name = record.event_time + '-' + record.digitalregister_id.name
            record.name = name

    @api.depends('digitalregister_id', 'digitalregister_id.partner_id')
    def _compute_partner_id(self):
        for record in self:
            partner_id = None
            if (record.digitalregister_id and
               record.digitalregister_id.partner_id):
                partner_id = record.digitalregister_id.partner_id
            record.partner_id = partner_id

    @api.model
    def update_access(self, access_name, summary, detail):
        resp = False
        if summary:
            access = self.search([('name', '=', access_name)])
            if access:
                vals = {'summary': summary}
                if detail:
                    vals['detail'] = detail
                access.write(vals)
                resp = True
        return resp
