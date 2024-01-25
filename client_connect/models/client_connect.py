# -*- coding: utf-8 -*-
from odoo import models, fields


class ClientConnect(models.Model):
    _name = 'client_connect'
    _description = 'Client Connect Information'

    database = fields.Char('Database')
    mail = fields.Char('Email')
    phone = fields.Char('Phone')
    company = fields.Char('Company')
    country = fields.Char('Country')
