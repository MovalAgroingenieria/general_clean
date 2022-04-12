# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import requests
import xml.etree.ElementTree as ET
from odoo import models, fields, api


class SimplecadastreModel(models.AbstractModel):
    _name = 'simplecadastre.model'
    _description = 'Simple Cadastre Model'

    # Size of the "rc1" part of a cadastral reference.
    SIZE_RC1 = 7

    # Size of the "rc2" part of a cadastral reference.
    SIZE_RC2 = 7

    # Cadastral URL to get the cadastral data of a parcel from its
    # cadastral reference.
    _url_cadastral_data = 'http://ovc.catastro.meh.es/ovcservweb/' + \
        'OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC?' + \
        'Provincia=&Municipio=&RC='

    # Cadastral URL to show the official form mapped to a cadastral
    # reference.
    _url_cadastral_form = 'https://www1.sedecatastro.gob.es/' + \
        'CYCBienInmueble/OVCListaBienes.aspx?del=&muni=&rc1=rc1val&rc2=rc2val'

    # Update cadastral area when entering cadastral reference?
    _automatic_update_cadastral_data = True

    cadastral_reference = fields.Char(
        string='Cadastral Reference',)

    cadastral_area = fields.Integer(
        string='Cadastral Area',
        compute='_compute_cadastral_area',)

    cadastral_link = fields.Char(
        string='Cadastral Link',
        default='',
        compute='_compute_cadastral_link',)

    def _compute_cadastral_area(self):
        for record in self:
            cadastral_area = 0
            if record.cadastral_reference:
                # Add try for exceptions on Cadastre services
                try:
                    resp_http_get = requests.get(
                        self._url_cadastral_data + record.cadastral_reference)
                    if resp_http_get.status_code == 200:
                        cadastral_data = ET.fromstring(resp_http_get.content)
                        prefix = ''
                        pos_closing = cadastral_data.tag.find('}')
                        if pos_closing != -1:
                            prefix = cadastral_data.tag[:pos_closing + 1]
                        number_of_items = int(cadastral_data[0][0].text)
                        if number_of_items == 1:
                            for item in cadastral_data.iter(prefix + 'ssp'):
                                area = int(item.text)
                                cadastral_area = cadastral_area + area
                except Exception:
                    cadastral_area = 0
            record.cadastral_area = cadastral_area

    def _compute_cadastral_link(self):
        length_cadastral_reference = self.SIZE_RC1 + self.SIZE_RC2
        for record in self:
            cadastral_link = ''
            if (record.cadastral_reference and
               len(record.cadastral_reference) == length_cadastral_reference):
                rc1 = record.cadastral_reference[:self.SIZE_RC1]
                rc2 = record.cadastral_reference[self.SIZE_RC2:]
                cadastral_link = \
                    self._url_cadastral_form.replace(
                        'rc1val', rc1).replace('rc2val', rc2)
            record.cadastral_link = cadastral_link

    @api.onchange('cadastral_reference')
    def _onchange_cadastral_reference(self):
        self._compute_cadastral_link()
        if self._automatic_update_cadastral_data:
            self._compute_cadastral_area()

    def action_show_cadastral_form(self):
        self.ensure_one()
        if self.cadastral_link:
            return {
                'type': 'ir.actions.act_url',
                'url': self.cadastral_link,
                'target': 'new',
            }

    def action_no_cadastral_info(self):
        self.ensure_one()
