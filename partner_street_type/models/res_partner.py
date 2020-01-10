# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    street_type = fields.Selection([
        ('AD', 'AD - ALDEA'),
        ('AG', 'AG - AGREGADO'),
        ('AL', 'AL - ALAMEDA'),
        ('AP', 'AP - APARTAMENTO'),
        ('AR', 'AR - ARRABAL'),
        ('AU', 'AU - AUTOPISTA'),
        ('AV', 'AV - AVENIDA'),
        ('AY', 'AY - ARROYO'),
        ('BJ', 'BJ - BAJADA'),
        ('BL', 'BL - BLOQUE'),
        ('BO', 'BO - BARRIO'),
        ('BR', 'BR - BARRANCO'),
        ('CD', 'CD - CORREGIDOR'),
        ('CG', 'CG - COLEGIO'),
        ('CH', 'CH - CHALET'),
        ('CI', 'CI - CINTURÓN'),
        ('CJ', 'CJ - CALLEJA'),
        ('CL', 'CL - CALLE'),
        ('CM', 'CM - CAMINO'),
        ('CN', 'CN - CONJUNTO'),
        ('CÑ', 'CÑ - CAÑADA'),
        ('CO', 'CO - COLONIA'),
        ('CP', 'CP - CAMPA'),
        ('CR', 'CR - CARRETERA'),
        ('CS', 'CS - CASERIO'),
        ('CT', 'CT - CUESTA'),
        ('CU', 'CU - CONJUNTO'),
        ('CY', 'CY - CARRIL'),
        ('DE', 'DE - DETRÁS'),
        ('DS', 'DS - DISEMINADO'),
        ('ED', 'ED - EDIFICIO'),
        ('EM', 'EM - EXTRAMUROS'),
        ('EN', 'EN - ENTRADA'),
        ('ER', 'ER - EXTRARRADIO'),
        ('ES', 'ES - ESCALINATA'),
        ('EX', 'EX - EXPLANADA'),
        ('FC', 'FC - FERROCARRIL'),
        ('FN', 'FN - FINCA'),
        ('GL', 'GL - GLORIETA'),
        ('GP', 'GP - DESCONOCIDA'),
        ('GR', 'GR - GRUPO'),
        ('GV', 'GV - GRAN VÍA'),
        ('HT', 'HT - HUERTA'),
        ('JR', 'JR - JARDINES'),
        ('LD', 'LD - LADO'),
        ('LG', 'LG - LUGAR'),
        ('MC', 'MC - MERCADO'),
        ('ML', 'ML - MUELLE'),
        ('MN', 'MN - MUNICIPIO'),
        ('MS', 'MS - MASÍA'),
        ('MT', 'MT - MONTE'),
        ('MZ', 'MZ - MANZANA'),
        ('PA', 'PA - PARCELA'),
        ('PB', 'PB - POBLADO'),
        ('PD', 'PD - PARTIDA'),
        ('PE', 'PE - PARAJE'),
        ('PG', 'PG - POLÍGONO'),
        ('PJ', 'PJ - PASAJE'),
        ('PM', 'PM - PÁRAMO'),
        ('PQ', 'PQ - PARQUE, PARROQUIA'),
        ('PR', 'PR - PROLONGACIÓN'),
        ('PS', 'PS - PASEO'),
        ('PT', 'PT - PUENTE'),
        ('PU', 'PU - PUERTA'),
        ('PZ', 'PZ - PLAZA'),
        ('QT', 'QT - QUINTA'),
        ('RB', 'RB - RAMBLA'),
        ('RC', 'RC - RINCÓN'),
        ('RD', 'RD - RONDA'),
        ('RM', 'RM - RAMAL'),
        ('RP', 'RP - RAMPA'),
        ('RR', 'RR - ROERA'),
        ('RU', 'RU - RUA'),
        ('SA', 'SA - SALIDA'),
        ('SB', 'SB - SUBIDA'),
        ('SD', 'SD - SENDA'),
        ('SL', 'SL - SOLAR'),
        ('SN', 'SN - SALÓN'),
        ('SU', 'SU - SUBIDA'),
        ('TN', 'TN - TERRENOS'),
        ('TO', 'TO - TORRENTE'),
        ('TR', 'TR - TRAVESÍA'),
        ('UR', 'UR - URBANIZACIÓN'),
        ('VD', 'VD - DESCONOCIDA'),
        ('VI', 'VI - VÍA'),
        ('VP', 'VP - VÍA PÚBLICA'),
        ('VR', 'VR - VEREDA')],
        string="Street type",
        default="CL",
        help="Acronym of street type according to the Spanish cadastre.")

    # Field just to show the acronnym
    street_type_show = fields.Char(
        string="Street type show",
        compute="_compute_street_type_show")

    # Field just to show the number
    street_number_show = fields.Char(
        string="Street number show",
        compute="_compute_street_number_show")

    @api.multi
    def _compute_street_type_show(self):
        for record in self:
            record.street_type_show = record.street_type

    @api.multi
    def _compute_street_number_show(self):
        for record in self:
            record.street_number_show = record.street_number

    # Overwrite original method from partner_street_number module
    # Each field is saved independently but they are injected into the
    # street field for printing.
    @api.depends('street_type', 'street_name', 'street_number', 'street3')
    def _get_street(self):
        for record in self:
            if record.street_type:
                street_type = record.street_type.lower().capitalize() + '. '
            else:
                street_type = ""
            if record.street_name:
                record.street_name = record.street_name
            else:
                record.street_name = ""
            if record.street_number:
                separator_1 = " "
                record.street_number = record.street_number
            else:
                separator_1 = ""
                record.street_number = ""
            if record.street3:
                separator_2 = ", "
                record.street3 = record.street3
            else:
                separator_2 = ""
                record.street3 = ""
            record.street = street_type + record.street_name + \
                separator_1 + record.street_number + separator_2 + \
                record.street3

    # Inhibit original reformatting method
    def _write_street(self):
        pass
