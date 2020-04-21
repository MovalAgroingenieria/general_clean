# -*- coding: utf-8 -*-
# 2019 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import unicodedata
from datetime import datetime


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    agency = fields.Selection([
        ('002', 'AIN'),
        ('003', 'ALBOCACE'),
        ('004', 'ALCALA'),
        ('005', 'ALCORA'),
        ('006', 'ALCUDIA'),
        ('007', 'ALFONDEG'),
        ('008', 'ALGIMIA'),
        ('009', 'ALMASSOR'),
        ('010', 'ALMEDIJA'),
        ('011', 'ALMENARA'),
        ('012', 'ALTURA'),
        ('013', 'ARAÑUEL'),
        ('014', 'ARES'),
        ('015', 'ARGELITA'),
        ('016', 'ARTANA'),
        ('001', 'ATZENETA'),
        ('017', 'AYODAR'),
        ('018', 'AZUEBAR'),
        ('019', 'BALLESTA'),
        ('020', 'BARRACAS'),
        ('022', 'BEJIS'),
        ('024', 'BENAFER'),
        ('025', 'BENAFIGO'),
        ('026', 'BENASSAL'),
        ('027', 'BENICARL'),
        ('028', 'BENICASS'),
        ('029', 'BENLLOCH'),
        ('021', 'BETXI'),
        ('030', 'BOJAR'),
        ('031', 'BORRIOL'),
        ('032', 'BURRIANA'),
        ('033', 'CABANES'),
        ('034', 'CALIG'),
        ('036', 'CANET'),
        ('037', 'CASTECAB'),
        ('038', 'CASTEFOR'),
        ('040', 'CASTELLO'),
        ('039', 'CASTENOV'),
        ('041', 'CASTILLO'),
        ('042', 'CATI'),
        ('043', 'CAUDIEL'),
        ('044', 'CERVERA'),
        ('054', 'CHIVA'),
        ('056', 'CHOVAR'),
        ('045', 'CINCTORR'),
        ('046', 'CIRAT'),
        ('047', 'CORACHAR'),
        ('048', 'CORTES'),
        ('049', 'COSTUR'),
        ('050', 'COVES'),
        ('051', 'CULLA'),
        ('057', 'ESLIDA'),
        ('058', 'ESPADILL'),
        ('059', 'FANZARA'),
        ('060', 'FIGUEROL'),
        ('061', 'FORCALL'),
        ('062', 'FREDES'),
        ('064', 'FUENAYOD'),
        ('063', 'FUENREIN'),
        ('065', 'GAIBIEL'),
        ('067', 'GELDO'),
        ('068', 'HERBES'),
        ('069', 'HIGUERAS'),
        ('070', 'JANA LA'),
        ('071', 'JERICA'),
        ('074', 'LLOSA LA'),
        ('072', 'LUCENA'),
        ('073', 'LUDIENTE'),
        ('075', 'MATA LA'),
        ('076', 'MATET'),
        ('077', 'MONCOFAR'),
        ('078', 'MONTAN'),
        ('079', 'MONTANEJ'),
        ('080', 'MORELLA'),
        ('081', 'NAVAJAS'),
        ('082', 'NULES'),
        ('083', 'OLOCAU'),
        ('084', 'ONDA'),
        ('085', 'OROPESA'),
        ('086', 'ORTELLS'),
        ('087', 'PALANQUE'),
        ('088', 'PAVIAS'),
        ('089', 'PEÑISCOL'),
        ('090', 'PINA'),
        ('093', 'POBLABEN'),
        ('094', 'POBLATOR'),
        ('091', 'PORTELL'),
        ('092', 'PUEBAREN'),
        ('095', 'RIBESALB'),
        ('096', 'ROSELL'),
        ('097', 'SACAÑET'),
        ('098', 'SALZADEL'),
        ('099', 'SANJORDI'),
        ('100', 'SANMATEU'),
        ('101', 'SANRAFAE'),
        ('102', 'SANTAMAG'),
        ('144', 'SANTJOAN'),
        ('103', 'SARRATEL'),
        ('104', 'SEGORBE'),
        ('105', 'SIERRA'),
        ('106', 'SONEJA'),
        ('107', 'SOTFERRE'),
        ('108', 'SUERAS'),
        ('109', 'TALES'),
        ('110', 'TERESA'),
        ('111', 'TIRIG'),
        ('112', 'TODOLELL'),
        ('113', 'TOGA'),
        ('114', 'TORAS'),
        ('115', 'TORO'),
        ('116', 'TORRALBA'),
        ('117', 'TORREBLA'),
        ('118', 'TORRECHI'),
        ('119', 'TORREMBE'),
        ('120', 'TORRENDO'),
        ('121', 'TRAIGUER'),
        ('122', 'USERAS'),
        ('124', 'VALLALBA'),
        ('125', 'VALLALMO'),
        ('123', 'VALLAT'),
        ('126', 'VALLDUXO'),
        ('127', 'VALLIBON'),
        ('128', 'VILAFAME'),
        ('129', 'VILAFRAN'),
        ('135', 'VILAREAL'),
        ('136', 'VILAVELL'),
        ('130', 'VILLAHER'),
        ('132', 'VILLALCO'),
        ('131', 'VILLAMAL'),
        ('134', 'VILLARCA'),
        ('133', 'VILLAVIV'),
        ('137', 'VILLORES'),
        ('138', 'VINAROS'),
        ('139', 'VISTABEL'),
        ('140', 'VIVER'),
        ('052', 'XERT'),
        ('053', 'XILXES'),
        ('055', 'XODOS'),
        ('141', 'ZORITA'),
        ('142', 'ZUCAINA'),
        ('143', 'REGALM')],
        string="Agency",
        help='This code identifies the agency or municipality that sends the '
            'delegated charge to OVR of Castellon.')

    @api.multi
    def set_agency_code_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'agency', self.agency)


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    ovrc_ref = fields.Char(
        string="OVRc reference",
        readonly=True,
        help='This number indicates the payment reference if it has been made '
            'by OVRc.')

    ovrc_sent = fields.Boolean(
        string="OVR done",
        readonly=True,
        help='Indicates whether this payment has already been added to an OVRc'
            ' payment file.')


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    ENCODING_NAME = '8859'
    ENCODING_TYPE = 'replace'

    def _get_agency_config_ovrc(self):
        code = self.env['ir.values'].get_default('account.config.settings',
                                                 'agency')
        if code:
            agency = dict(self.env['account.config.settings'].fields_get(
                allfields=['agency'])['agency']['selection'])[code]
        else:
            agency = "Unconfigured"
        return agency

    payment_mode_name = fields.Char(
        compute='_compute_payment_mode_name',
        string="Payment mode name")

    error_mode = fields.Selection([
        ('strict', 'Strict'),
        ('permissive', 'Permissive')],
        string="Error mode",
        default="strict",
        help='Strict mode does not allow errors. The permissive mode allows '
             'errors but they are collected in the Errors tab.')

    errors_found = fields.Text(
        string='Errors',
        readonly=True)

    agency = fields.Char(
        string="Agency",
        default=_get_agency_config_ovrc,
        compute="_compute_agency",
        readonly=True,
        help='This code identifies the agency or municipality that sends the '
            'delegated charge to OVRc.\nThis parameter is set in the '
            'accounting configuration.')

    income_type = fields.Selection([
        ('ZCRAL', 'ZCRAL - EX.W.U.A ALMASSORA'),
        ('ZCRALM', 'ZCRALM - EX.W.U.A ALMASSORA FINES AND PENALTIES')],
        string="Income type",
        help="Income type. It will be applied to all transactions.",
        default="ZCRAL")

    concept_code = fields.Selection([
        ('3400', 'FEE DISTRIBUTION DELIVERY 1ST SEMESTER'),
        ('3401', 'FEE DISTRIBUTION DELIVERY 2ND SEMESTER'),
        ('3408', 'CLEANING IRRIGATION DITCHES'),
        ('3406', 'FINES AND INDEMNIFICATIONS JURY OF IRRIGATIONS'),
        ('3407', 'IRRIGATION DITCH WORKS'),
        ('3405', 'BORDER IRRIGATION'),
        ('3402', 'LOCATED IRRIGATION 1-10 A 28-2'),
        ('3403', 'LOCATED IRRIGATION 1-3  A 30-6'),
        ('3404', 'LOCATED IRRIGATION 1-7 A 30-9')],
        string="Concept",
        help="Concept. It will be applied to all transactions.")

    exaction_type = fields.Selection([
        ('RB', 'Receipt'),
        ('ID', 'Settlement')],
        string="Exaction type",
        help="Type of exaction. It will be applied to all transactions.",
        default="RB")

    receipt_period = fields.Selection([
        ('1', '1 - First quarter, semester, etc'),
        ('2', '2 - Second quarter, semester, etc'),
        ('3', '3 - Third quarter, four-month, etc'),
        ('4', '4 - Fourth quarter, etc')],
        string="Period",
        help='Coverage time. Example: 1, if it is 1st quarter, semester, etc.'\
            '\nIt will be applied to all transactions.',
        default="1")

    @api.depends('payment_mode_id')
    def _compute_payment_mode_name(self):
        # @INFO: payment mode name OVRc (mandatory)
        self.payment_mode_name = self.payment_mode_id.name

    @api.depends('payment_mode_name')
    def _compute_agency(self):
        self.agency = self._get_agency_config_ovrc()

    @api.multi
    def generate_payment_file(self):
        self.ensure_one()
        _log = logging.getLogger(self.__class__.__name__)
        pay_method = self.payment_method_id

        if pay_method.code != 'debit_ovrc':
            return super(AccountPaymentOrder, self).generate_payment_file()

        # Selectioable fields
        # Agency name (CodMunicipio)
        # Position [01-08] Length 08
        agency_name_raw = self.agency
        agency_name = agency_name_raw[:8].ljust(8)

        # Income type code (CodTipoIngreso)
        # Position [09-15] Length 07
        income_type_raw = self.income_type
        income_type = income_type_raw[:7].ljust(7)

        # Concept code 1 (CodCon1)
        # Position [668-672] Length 05
        concept_code1_raw = self.concept_code
        concept_code1 = str(concept_code1_raw).ljust(5)

        # Receipt period (PeriodoRecibo)
        # Position [596-601] Length 06
        # @INFO: Periodo de cobertura (Ejemplo: 1, si es 1er trimenestre, etc)
        receipt_period_raw = self.receipt_period
        receipt_period = str(receipt_period_raw).ljust(6)

        # Type Exaction (TipoExaccion)
        # Position [486-487] Length 02
        exaction_type = str(self.exaction_type)

        # Optional fields
        lastname = str(' ' * 25)  # Position [90-114] Length 25
        lastname2 = str(' ' * 25)  # Position [115-139] Length 25
        firstname = str(' ' * 20)  # Position [140-139] Length 20
        street_code = str(' ' * 5)  # Position [165-169] Length 05
        province_name = str(' ' * 50)  # Position [175-224] Length 50
        other_address_params = str(' ' * 42)  # Position [334-375] Length 42
        aceptance_date = str(' ' * 19)  # Position [571-589] Length 19
        # Position [689-1185] Length 497 (With 0 in amount position)
        not_used_exercises = str((' ' * 55 + '0' + ' ' * 15) * 7)  

        # Reset variables
        bank_lines = ""
        entry_num = 0
        errors = ""
        error_num = 0

        # Iterate over bank lines
        for line in self.bank_line_ids:

            # Entry number (padded up to 6)
            entry_num += 1
            entry_num_padded = str(entry_num).zfill(6)

           # Check if bank line is already done
            if line.ovrc_sent:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed,the bank line %s "
                          "seems that it has already been sent \n" %
                          (entry_num_padded, line.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed,the bank line %s "
                          "seems that it has already been sent" %
                          (entry_num_padded, line.name)))

            # Person type (TipoPersona)
            # Position [16-16] Length 01
            if line.partner_id.company_type == 'company':
                person_type = "J"
            else:
                person_type = "F"

            # Vat (NIF)
            # Position [17-28] Length 12
            # @TODO: sliced?? str(line.partner_id.vat[2:]).ljust(12)
            if line.partner_id.vat:
                vat = line.partner_id.vat[2:][:-1].ljust(12)
                # Vat control digit (dcNIF)
                # Position [29-29] Length 01
                vat_cd = line.partner_id.vat[-1]
            else:
                if self.error_mode == 'permissive':
                    vat = str(' ' * 12)
                    vat_cd = str(' ')
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, vat not found for "
                          "partner %s \n" % (entry_num_padded,
                                          line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, vat not found for "
                          "partner %s." % (entry_num_padded,
                                           line.partner_id.name)))

            # Full name (NombreCompleto)
            # Position [30-89] Length 60
            if person_type == "F":
                if line.partner_id.lastname:
                    full_name_raw = line.partner_id.lastname + ' '
                    if line.partner_id.lastname2:
                        full_name_raw += line.partner_id.lastname2 + ' '
                    if line.partner_id.firstname:
                        full_name_raw += line.partner_id.firstname
                    full_name = full_name_raw[:60].ljust(60).upper()
                else:
                    full_name = False

            if person_type == "J":
                if line.partner_id.name:
                    full_name_raw = \
                        line.partner_id.name.replace(".", "").replace(",", " ")
                    full_name = \
                        full_name = full_name_raw[:60].ljust(60).upper()
                else:
                    full_name = False

            if not full_name:
                if self.error_mode == 'permissive':
                    full_name = str(" " * 60)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, lastname not found "
                          "for partner %s \n" % (entry_num_padded,
                                              line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, lastname not found "
                          "for partner %s" % (entry_num_padded,
                                              line.partner_id.name)))

            if line.partner_id.city:
                city_name = city_name2 = city_name_simplified = \
                    city_name_simplified2 = ""
                if '(' in line.partner_id.city:
                    city_name = line.partner_id.city[
                        line.partner_id.city.find(
                            "(")+1:line.partner_id.city.find(")")]
                    city_name2 = line.partner_id.city.split('(')[0]
                elif '/' in line.partner_id.city:
                    city_names = line.partner_id.city.split('/')
                    city_name = city_names[0]
                    city_name2 = city_names[1]
                else:
                    city_name = line.partner_id.city

                city_name_simplified = \
                    unicodedata.normalize(
                        'NFKD', city_name).encode(
                            self.ENCODING_NAME, self.ENCODING_TYPE).upper()
                if city_name2:
                    city_name_simplified2 = \
                        unicodedata.normalize(
                            'NFKD', city_name2).encode(
                                self.ENCODING_NAME,
                                self.ENCODING_TYPE).upper()
                else:
                    city_name_simplified2 = ""

                ine_codes = \
                    self.env['res.ine.code'].search(
                        ['|', '|', '|', '|', '|',
                         ('city_name_simplified', '=',
                          city_name_simplified),
                         ('city_name_aka_simplified', '=',
                          city_name_simplified),
                         ('city_name_simplified', '=',
                          city_name_simplified2),
                         ('city_name_aka_simplified', '=',
                          city_name_simplified2),
                         ('city_name_reordered_simplified', '=',
                          city_name_simplified),
                         ('city_name_reordered_simplified', '=',
                          city_name_simplified2)])

                if ine_codes:
                    # Province code (CodPro)
                    # Position [160-161] Length 02
                    province_code = str(ine_codes.ine_code_province).zfill(2)
                    # County code (CodMun)
                    # Position [162-164] Length 03
                    county_code = str(ine_codes.ine_code_city).zfill(3)
                    # County name (NombreMunicipio)
                    # Position [225-274] Length 50
                    county_name = city_name_simplified[:50].ljust(50)
                else:
                    if self.error_mode == 'permissive':
                        province_code = str(' ' * 2)
                        county_code = str(' ' * 3)
                        county_name = str(' ' * 50)
                        error_num += 1
                        errors += '[' + str(error_num).zfill(4) + '] ' + \
                            _("The entry number %s has failed, INE codes not "
                              "found for city %s \n" % (entry_num_padded,
                                                        line.partner_id.city))
                    else:
                        raise ValidationError(
                            _("The entry number %s has failed, INE codes not "
                              "found for city %s" % (entry_num_padded,
                                                     line.partner_id.city)))
            else:
                if self.error_mode == 'permissive':
                    county_name = str(' ' * 50)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, city not found for "
                          "partner %s \n" % (entry_num_padded,
                                             line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, city not found for "
                          "partner %s" % (entry_num_padded,
                                          line.partner_id.name)))

            # Zip (CodigoPostal)
            # Position [170-174] Length 05
            if line.partner_id.zip:
                zip_code = str(line.partner_id.zip)
            else:
                if self.error_mode == 'permissive':
                    zip_code = str(' ' * 5)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, ZIP not found for "
                          "partner %s \n" % (entry_num_padded,
                                          line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, ZIP not found for "
                          "partner %s" % (entry_num_padded,
                                          line.partner_id.name)))

            # Street type (SiglasCalle)
            # Position [275-279] Length 05
            if line.partner_id.street_type_id:
                street_type_raw = \
                    line.partner_id.street_type_id.abbreviation
                street_type = street_type_raw.ljust(5)
            else:
                if self.error_mode == 'permissive':
                    street_type = str(" " * 5)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, street type not "
                          "found for partner %s \n" % (entry_num_padded,
                                                       line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, street type not "
                          "found for partner %s" % (entry_num_padded,
                                                    line.partner_id.name)))

            # Street name (NombreCalle)
            # Position [280-329] Length 50
            if line.partner_id.street:
                street_name = line.partner_id.street.ljust(50).upper()
            else:
                if self.error_mode == 'permissive':
                    street_name = str(" " * 50)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, street not found "
                          "for partner %s \n" % (entry_num_padded,
                                              line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, street not found "
                          "for partner %s" % (entry_num_padded,
                                              line.partner_id.name)))

            # Street number (NumeroCalle)
            # Position [330-333] Length 04
            if line.partner_id.street_num:
                street_number_raw = filter(lambda x: x.isdigit(),
                                           line.partner_id.street_num)
                street_number = str(street_number_raw).ljust(4)
            else:
                street_number = str(' ' * 4)

            # Tax object description (DescObjetoTrib)
            # Position [376-425] Length 50
            if line.communication:
                tax_object_desc = line.communication.ljust(50)

            # Taxable event description (DescripHechoImponible)
            # Position [426-485] Length 60
            # @TODO: or not used or other information (for app, not user)
            tax_event_desc = str(' ' * 60)

            # Value number (NumValor)
            # Position [488-498] Length 11
            value_number = self.env['ir.sequence'].next_by_code(
                'ovrc_seq_value_number')

            # Associate this number to each bank line and set as done
            line.ovrc_ref = value_number
            line.ovrc_sent = True

            # Entity reference (Referencia)
            # Position [499-522] Length 24
            # @TODO: Referencia, Número Fijo Ayto., Referencia Objeto Tributario
            entity_ref = str(' ' * 24)

            # Remittance number (NumRemesa)
            # Position [523-532] Length 10
            # @TODO: payment name? Final part of filename?
            remittance_number = str(self.name[:7]).ljust(10)


            for l in line.payment_line_ids:
                if line.name == l.bank_line_id.name:
                    # Voluntary end date (FecFinVoluntaria)
                    # Position [533-551] Length 19
                    # @INFO: Format 7/8/2018 0:00:00
                    # Set voluntary_end_date to l.move_line_id.date_maturity
                    voluntary_end_date = datetime.strptime(
                        l.move_line_id.date_maturity, '%Y-%m-%d'
                        ).strftime("%d/%m/%Y").ljust(19)

                    # Accrual date (FecDevengo)
                    # Position [1186-1204] Length 19
                    # @INFO: Format 7/8/2018 0:00:00
                    # Set Accrual date to invoice date
                    accrual_date = datetime.strptime(
                        l.move_line_id.date, '%Y-%m-%d'
                        ).strftime("%d/%m/%Y").ljust(19)

                    # Award providence date (FecProvApremio)
                    # Position [552-570] Length 19
                    # @TODO
                    award_prov_date = str(' ' * 19)

                    # Receipt year (AnyoRecibo)
                    # Position [590-595] Length 06
                    # @INFO: Año del periodo de cobertura (Ejercicio devengo del Recibo)
                    receipt_year = datetime.strptime(
                        l.move_line_id.date, '%Y-%m-%d'
                        ).strftime("%Y").ljust(6)

            if not voluntary_end_date or not accrual_date or not receipt_year:
                if self.error_mode == 'permissive':
                    voluntary_end_date = str(" " * 19)
                    accrual_date = str(" " * 19)
                    receipt_year = str(" " * 6)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, invoices dates "
                          "failed for partner %s \n" % (entry_num_padded,
                                                        line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, invoices dates "
                          "failed for partner %s" % (entry_num_padded,
                                                     line.partner_id.name)))

            # Total amount (ImporteTotal)
            # Position [602-617] Length 16
            # @INFO: 10,00 euros según Ordenanza SGIR
            total_amount_raw = "%0.2f" % (line.amount_currency,)
            total_amount = total_amount_raw.replace('.', ',').ljust(16)

            # Exercise 1 (Ejer1)
            # Position [618-667] Length 50
            # @TODO: Free text for user
            exercise1_raw = receipt_year.strip()
            exercise1 = exercise1_raw.ljust(50)

            # Concept1 amount (Imp1)
            # Position [673-688] Length 16
            # @INFO: equal to total_amount
            concept1_amount = total_amount

            # Log bank line fields with length [and expected length]
            _log.info('NEW BANK LINE. Number %s #############################'
                      % str(entry_num).zfill(2))
            _log.info('agency_name                      (length %s [008]): %s'
                      % (str(len(agency_name)).zfill(3), agency_name))
            _log.info('income_type                      (length %s [007]): %s'
                      % (str(len(income_type)).zfill(3), income_type))
            _log.info('person_type                      (length %s [001]): %s'
                      % (str(len(person_type)).zfill(3), person_type))
            _log.info('vat                              (length %s [012]): %s'
                      % (str(len(vat)).zfill(3), vat))
            _log.info('vat_cd                           (length %s [001]): %s'
                      % (str(len(vat_cd)).zfill(3), vat_cd))
            _log.info('full_name                        (length %s [060]): %s'
                      % (str(len(full_name)).zfill(3), full_name))
            _log.info('lastname                         (length %s [025]): %s'
                      % (str(len(lastname)).zfill(3), lastname))
            _log.info('lastname2                        (length %s [025]): %s'
                      % (str(len(lastname2)).zfill(3), lastname2))
            _log.info('firstname                        (length %s [020]): %s'
                      % (str(len(firstname)).zfill(3), firstname))
            _log.info('province_code                    (length %s [002]): %s'
                      % (str(len(province_code)).zfill(3), province_code))
            _log.info('county_code                      (length %s [003]): %s'
                      % (str(len(county_code)).zfill(3), county_code))
            _log.info('street_code                      (length %s [005]): %s'
                      % (str(len(street_code)).zfill(3), street_code))
            _log.info('zip_code                         (length %s [005]): %s'
                      % (str(len(zip_code)).zfill(3), zip_code))
            _log.info('province_name                    (length %s [050]): %s'
                      % (str(len(province_name)).zfill(3), province_name))
            _log.info('county_name                      (length %s [050]): %s'
                      % (str(len(county_name)).zfill(3), county_name))
            _log.info('street_type                      (length %s [005]): %s'
                      % (str(len(street_type)).zfill(3), street_type))
            _log.info('street_name                      (length %s [050]): %s'
                      % (str(len(street_name)).zfill(3), street_name))
            _log.info('street_number                    (length %s [004]): %s'
                      % (str(len(street_number)).zfill(3), street_number))
            _log.info('other_address_params             (length %s [042]): %s'
                      % (str(len(other_address_params)).zfill(3),
                         other_address_params))
            _log.info('tax_object_desc                  (length %s [050]): %s'
                      % (str(len(tax_object_desc)).zfill(3), tax_object_desc))
            _log.info('tax_event_desc                   (length %s [060]): %s'
                      % (str(len(tax_event_desc)).zfill(3), tax_event_desc))
            _log.info('exaction_type                    (length %s [002]): %s'
                      % (str(len(exaction_type)).zfill(3), exaction_type))
            _log.info('value_number                     (length %s [011]): %s'
                      % (str(len(value_number)).zfill(3), value_number))
            _log.info('entity_ref                       (length %s [024]): %s'
                      % (str(len(entity_ref)).zfill(3), entity_ref))
            _log.info('remittance_number                (length %s [050]): %s'
                      % (str(len(remittance_number)).zfill(3),
                         remittance_number))

            _log.info('voluntary_end_date               (length %s [019]): %s'
                      % (str(len(voluntary_end_date)).zfill(3),
                         voluntary_end_date))
            _log.info('award_prov_date                  (length %s [019]): %s'
                      % (str(len(award_prov_date)).zfill(3),
                         award_prov_date))
            _log.info('aceptance_date                   (length %s [019]): %s'
                      % (str(len(aceptance_date)).zfill(3),
                         aceptance_date))
            _log.info('receipt_year                     (length %s [006]): %s'
                      % (str(len(receipt_year)).zfill(3), receipt_year))

            _log.info('receipt_period                   (length %s [006]): %s'
                      % (str(len(receipt_period)).zfill(3), receipt_period))
            _log.info('total_amount                     (length %s [016]): %s'
                      % (str(len(total_amount)).zfill(3), total_amount))
            _log.info('exercise1                        (length %s [050]): %s'
                      % (str(len(exercise1)).zfill(3), exercise1))
            _log.info('concept_code1                    (length %s [005]): %s'
                      % (str(len(concept_code1)).zfill(3), concept_code1))
            _log.info('concept1_amount                  (length %s [016]): %s'
                      % (str(len(concept1_amount)).zfill(3), concept1_amount))
            _log.info('not_used_exercises               (length %s [497]): %s'
                      % (str(len(not_used_exercises)).zfill(3),
                         not_used_exercises))
            _log.info('accrual_date                     (length %s [019]): %s'
                      % (str(len(accrual_date)).zfill(3), accrual_date))

            # Construct bank line
            bank_line = agency_name + income_type + person_type + vat + \
                vat_cd + full_name + lastname + lastname2 + firstname + \
                province_code + county_code + street_code + zip_code + \
                province_name + county_name + street_type + street_name + \
                street_number + other_address_params + tax_object_desc + \
                tax_event_desc + exaction_type + value_number + entity_ref + \
                remittance_number + voluntary_end_date + award_prov_date + \
                aceptance_date + receipt_year + receipt_period + \
                total_amount + exercise1 + concept_code1 + concept1_amount + \
                not_used_exercises + accrual_date + "\r\n"

            _log.info('FULL BANK LINE                 (length %s [1204]): %s'
                      % (str(len(bank_line)).zfill(4),
                         bank_line.encode(self.ENCODING_NAME,
                                          self.ENCODING_TYPE)))

            # Add to bank_lines
            bank_lines += bank_line.encode(self.ENCODING_NAME,
                                           self.ENCODING_TYPE)


        # Encode and send to the file
        payment_file_str = bank_lines

        # Set filename
        filename = agency_name.strip() + receipt_year.strip() + '_' + \
            remittance_number.strip() + "v2.txt"

        # Fill error tab
        if self.error_mode == 'permissive':
            self.errors_found = errors

        return payment_file_str, filename


#     @api.multi
#     def action_done_cancel(self):
#         for order in self:
#             if order.payment_mode_id.name == 'OVRc':
#                 for bline in order.bank_line_ids:
#                     invoice = self.env['account.invoice'].search([
#                             ('number', '=', bline.communication)])
#                     invoice.write({
#                             'in_ovrc': False,
#                             'ovrc_ref': False,
#                         })
#         return super(AccountPaymentOrder, self).action_done_cancel()
