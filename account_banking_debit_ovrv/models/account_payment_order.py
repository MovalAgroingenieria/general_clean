# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import unicodedata
from datetime import datetime


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    agency_code = fields.Selection([
        ('312', '312 - C.R. SECTOR I - LOS TOLLOS')],
        string="Agency Code",
        help="This code identifies the agency or municipality that sends\
            the delegated charge to OVR of Valencia.")

    @api.multi
    def set_agency_code_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'agency_code', self.agency_code)



class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    ovrv_ref = fields.Char(
        string="OVR reference",
        readonly=True,
        help='This number indicates the payment reference if it has been made '
            'by OVRv')

    ovrv_sent = fields.Boolean(
        string="OVR done",
        readonly=True,
        help='Indicates whether this payment has already been added to one '
            'OVRv payment file')


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    ENCODING_NAME = '8859'
    ENCODING_TYPE = 'replace'

    def _get_agency_config_ovrv(self):
        code = self.env['ir.values'].get_default('account.config.settings',
                                                 'agency_code')
        if code:
            agency = dict(self.env['account.config.settings'].fields_get(
                allfields=['agency_code'])['agency_code']['selection'])[code]
        else:
            agency = "Unconfigured"
        return agency

    payment_mode_name = fields.Char(
        compute='_compute_payment_mode_name',
        string="Payment mode name")

    agency = fields.Char(
        string="Agency",
        default=_get_agency_config_ovrv,
        compute="_compute_agency",
        readonly=True,
        help='This code identifies the agency or municipality that sends the '
            'delegated charge to OVRv.\nThis parameter is set in the '
            'accounting configuration.')

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

    debt_period = fields.Selection([
        ('E', 'Executive')],
        string="Debt period",
        readonly=True,
        default="E",
        help='Period in which debts should be managed.\nAt this time only the '
            'Executive period is available.')

    income_type = fields.Selection([
        ('609', 'T609 - Agrarian services')],
        string="Income type",
        readonly=True,
        default="609",
        help='Type of income. Depends on the agency and will apply to all '
            'transactions.')

    concept_code = fields.Selection([
        ('603', '603 - Community expenses'),
        ('778', '778 - Irrigation water'),
        ('779', '779 - Drip irrigation')],
        string="Concept",
        default="603",
        help='Concept by which the settlement is made. Depends on the agency '
            'and type of income. Will apply to all transactions.')

    settlement_year = fields.Selection([
        ('20', '2020'), ('21', '2021'),
        ('22', '2022'), ('23', '2023'),
        ('24', '2024'), ('25', '2025'),
        ('26', '2026'), ('27', '2027'),
        ('28', '2028'), ('29', '2029')],
        string='Settlement year',
        default=datetime.today().strftime("%y"))

    periodicity = fields.Selection([
        ('0', '0 - Annual'),
        ('1', '1 - First emission'),
        ('2', '2 - Second emission'),
        ('3', '3 - Third emission'),
        ('4', '4 - Fourth emission'),
        ('5', '5 - Fifth emission'),
        ('6', '6 - Sixth emission'),
        ('7', '7 - Seventh emission'),
        ('8', '8 - Eighth emission'),
        ('9', '9 - Ninth emission')],
        string='Periodicity',
        default="0")

    generation_date = fields.Date(
        string='Generation date',
        default=datetime.today())

    add_direct_debit = fields.Boolean(
        string='Add direct debit',
        default=False)

    surcharge_percentage = fields.Selection([
        ('0', 'Not apply'),
        ('0.05', '5%'),
        ('0.10', '10%'),
        ('0.20', '20%')],
        string='Surcharge',
        default="0")

    @api.depends('payment_mode_id')
    def _compute_payment_mode_name(self):
        self.payment_mode_name = self.payment_mode_id.name

    @api.depends('payment_mode_name')
    def _compute_agency(self):
        self.agency = self._get_agency_config_ovrv()


    @api.multi
    def generate_payment_file(self):
        self.ensure_one()
        _log = logging.getLogger(self.__class__.__name__)
        pay_method = self.payment_method_id

        if pay_method.code != 'debit_ovrv':
            return super(AccountPaymentOrder, self).generate_payment_file()

        # Declare error vars
        self.errors_found = ""
        errors = ""
        error_num = 0

        # Reset variables
        entry_num = 0
        r98_amount_total_sum = 0.0
        payment_file_str_raw = ""

        # Registre 51 (Length 82)
        registre_51 = ""

        # r51_type - Position 1-2 (Length 2)
        r51_type = '51'

        # r51_year - Position 3-4 (Length 2)
        # @INFO: Dos últimos dígitos del año de la liquidación tributaria
        r51_year = self.settlement_year

        # r51_agency code - Position 5-7 (Length 3)
        r51_agency_code = self.env['ir.values'].get_default(
            'account.config.settings', 'agency_code')

        # r51_income_type - Position 8-10 (Length 3)
        r51_income_type = self.income_type

        # r51_value_type - Position 11-11 (Length 1)
        # @INFO: Only 4 (Certificaciones de descubierto en ejecutiva)
        r51_value_type = "4"

        # r51_issuing_ref - Position 12-18 (Length 7)
        # @INFO: Número de recibo que asigne el ayto (payment name?)
        r51_issuing_ref = str(self.name[:7]).ljust(7)

        # r51_subconcept_num - Position 49-50 (Length 2)
        # @INFO: always will only one subconcept
        r51_subconcept_num = "01"

        # Registre 52 (Length 82)
        registre_52 = ""

        # r52_type - Position 1-2 (Length 2)
        r52_type = '52'

        # Registre 53 (Length 82)
        registre_53 = ""

        # r53_type - Position 1-2 (Length 2)
        r53_type = '53'

        # Registre 54 (Length 82)
        registre_54 = ""

        # r54_type - Position 1-2 (Length 2)
        r54_type = '54'

        # r54_concept_code - Position 3-5 (Length 3)
        r54_concept_code = self.concept_code

        # Registre 55 (Length 82)
        registre_55 = ""

        # r55_type - Position 1-2 (Length 2)
        r55_type = '55'

        # Registre 66 (Length 82)
        registre_66 = ""

        # r66_type - Position 1-2 (Length 2)
        r66_type = '66'

        # r66_content - Position 3-82 (Length 80)
        r66_content_raw = "To be filled"
        r66_content = r66_content_raw[:80].ljust(80)

       # Registre 98 (Length 82)
        registre_98 = ""

        # r98_type - Position 1-2 (Length 2)
        r98_type = '98'

        # r98_number_subconcepts - Position 23-25 (Length 3)
        r98_number_subconcepts = "001"

        # r98_generation_date - Position 26-31 (Length 6)
        r98_generation_date = datetime.strptime(
            self.generation_date, "%Y-%m-%d").strftime("%d%m%y")

        # r98_rest - Position 43-82 (Length 40)
        r98_rest = str(' ' * 40)

       # Registre 99 (Length 82)
        registre_99 = ""

        # r99_type - Position 1-2 (Length 2)
        r99_type = '99'


        for line in self.bank_line_ids:

            # Entry number (used to count num of registres)
            entry_num += 1
            entry_num_padded = str(entry_num).zfill(6)


            # Check if bank line is already done
            if line.ovrv_sent:
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

            # r51_fixed_num - Position 19-38 (Length 20)
            # @INFO: número único que identifica al valor (sequence)
            r51_fixed_num = self.env['ir.sequence'].next_by_code(
                'ovrv_seq_r51_fix_number')

            # Associate this number to each bank line and set as done
            line.ovrv_ref = r51_fixed_num
            line.ovrv_sent = True

            # r51_personality - Position 39-39 (Length 1)
            if line.partner_id.company_type == 'company':
                r51_personality = "J"
            else:
                r51_personality = "F"

            # r51_vat - Position 40-48 (Length 9)
            # @TODO: Check format
            if line.partner_id.vat:
                r51_vat = str(line.partner_id.vat[2:]).ljust(9)
            else:
                if self.error_mode == 'permissive':
                    r52_vat = str(" " * 9)
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

            # r52_name - Position 3-42 (Length 40)
            # @INFO Apellido_1o Apellido_2o, Nombre
            if r51_personality == "F":
                if line.partner_id.lastname:
                    r52_name_raw = line.partner_id.lastname
                    if line.partner_id.lastname2:
                        r52_name_raw += ' ' + line.partner_id.lastname2
                    if line.partner_id.firstname:
                        r52_name_raw += ', ' + line.partner_id.firstname
                    r52_name = r52_name_raw[:40].ljust(40)
                else:
                    r52_name = False

            if r51_personality == "J":
                if line.partner_id.name:
                    r52_name_raw = \
                        line.partner_id.name.replace(".", "").replace(",", " ")
                    r52_name = r52_name_raw[:40].ljust(40)
                else:
                    r52_name = False

            if not r52_name:
                if self.error_mode == 'permissive':
                    r52_name = str(" " * 40)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, name not found for "
                          "partner %s \n" % (entry_num_padded,
                                             line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, name not found for "
                          "partner %s \n" % (entry_num_padded,
                                             line.partner_id.name)))

            # r52_street_type - Position 43-44 (Length 2)
            if line.partner_id.street_type_id:
                r52_street_type = line.partner_id.street_type_id.abbreviation
            else:
                if self.error_mode == 'permissive':
                    r52_street_type = str(" " * 2)
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

            # r52_address - Position 45-82 (Length 38)
            if line.partner_id.street:
                r52_address_raw = line.partner_id.street
                if line.partner_id.street_num:
                    r52_address_raw += ' ' + line.partner_id.street_num
                r52_address = r52_address_raw[:38].ljust(38)
            else:
                if self.error_mode == 'permissive':
                    r52_address = str(" " * 38)
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, address not found "
                          "for partner %s \n" % (entry_num_padded,
                                              line.partner_id.name))
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, address not found "
                          "for partner %s" % (entry_num_padded,
                                              line.partner_id.name)))

            # r53_ine_province - Position 3-4 (Length 2)
            # r53_ine_county - Position 5-7 (Length 3)
            # r53_zip - Position 8-12 (Length 5)
            # r53_county - Position 13-37 (Length 25)
            if line.partner_id.city:
                r53_county_raw = line.partner_id.city
                r53_county = r53_county_raw[:25].ljust(25)

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
                    r53_ine_province = \
                        str(ine_codes.ine_code_province).zfill(2)
                    r53_ine_county = str(ine_codes.ine_code_city).zfill(3)
                else:
                    if self.error_mode == 'permissive':
                        r53_ine_province = str(' ' * 2)
                        r53_ine_county = str(' ' * 3)
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
                    r53_county = str(' ' * 25)
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

            # r53_zip - Position 8-12 (Length 5)
            if line.partner_id.zip:
                r53_zip = str(line.partner_id.zip)
            else:
                if self.error_mode == 'permissive':
                    r53_zip = str(' ' * 5)
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

            # r53_tax_object - Position 38-82 (Length 45)
            # @INFO: Objeto Tributario (Domicilio Tributario, Parcela, Matrícula).
            r53_tax_object_raw = line.communication
            r53_tax_object = r53_tax_object_raw.ljust(45)

            # r54_amount - Position 6-15 (Length 10)
            # @INFO: 8 enteros y 2 decimales sin coma
            r54_amount_raw = "%0.2f" % (line.amount_currency,)
            r54_amount = r54_amount_raw.replace('.', '').zfill(10)

            # Construct CCC from IBAN
            # @INFO: We get the account number associated to mandate_id
            if line.mandate_id and \
               line.mandate_id.partner_id.mandate_count > 0 and \
               self.add_direct_debit:
                iban = line.mandate_id.partner_bank_id.sanitized_acc_number
                if iban and len(iban) != 0:
                    # bank_code - Position 3-6 (Length 4)
                    r55_bank_code = str(iban[4:8])
                    # bank_office code - Position 7-10 (Length 4)
                    r55_bank_office_code = str(iban[8:12])
                    # bank_control_digit - Position 11-12 (Length 2)
                    r55_bank_control_digit = str(iban[12:14])
                    # bank_acc_number - Position 13-22 (Length 10)
                    r55_bank_acc_number = str(iban[14:]).ljust(10)
                    # bank_account_holder - Position 23-62 (Length 40)
                    r55_bank_acc_holder = r52_name
                    # bank_account_holder - Position 63-63 (Length 1)
                    r55_bank_acc_holder_personality = r51_personality
                    # bank_account_holder - Position 64-72 (Length 9)
                    r55_bank_acc_holder_vat = r51_vat
                    # bank_rest - Position 73-82 (Length 10)
                    r55_bank_rest = str(' ' * 10)

                    registre_55 = r55_type + r55_bank_code + \
                        r55_bank_office_code + r55_bank_control_digit + \
                        r55_bank_acc_number + r55_bank_acc_holder + \
                        r55_bank_acc_holder_personality + \
                        r55_bank_acc_holder_vat + r55_bank_rest + "\r\n"
            else:
                # If no mandate, no registre_55
                r55_bank_code = r55_bank_office_code = \
                    r55_bank_control_digit = r55_bank_acc_number = \
                    r55_bank_acc_holder = r55_bank_acc_holder_personality = \
                    r55_bank_acc_holder_vat = r55_bank_rest = ""
                registre_55 = ""

            # Add to r98_amount_total
            r98_amount_total_sum += line.amount_currency

            # Notification_date Position 77-82 (Length 8)
            # @INFO: - la fecha en la cual se ha producido la última notificación, en el formato ddmmaa.
            #        - No providenciados”  En este caso fecha de NOTIFICACION DE LA LIQUIDACION (invoice date?)
            for l in line.payment_line_ids:
                if line.name == l.bank_line_id.name:
                    # Set notification date to invoice date and get settlement year
                    r51_notification_date = datetime.strptime(l.move_line_id.date,
                                          '%Y-%m-%d').strftime("%d%m%y")

            # r51_amount_main - Position 60-68 (Length 9)
            # @INFO: 7 enteros y 2 decimales sin coma
            r51_amount_main_raw = "%0.2f" % (line.amount_currency,)
            r51_amount_main = r51_amount_main_raw.replace('.', '').zfill(9)

            # r51_amount_charge - Position 69-76 (Length 8) 
            # @INFO: 6 enteros y 2 decimales sin coma
            # @TODO: porcentaje ??
            r51_amount_charge_cal = line.amount_currency * \
                float(self.surcharge_percentage)
            r51_amount_charge_raw = "%0.2f" % (r51_amount_charge_cal,)
            r51_amount_charge = r51_amount_charge_raw.replace('.', '').zfill(8)

            # r51_amount_total - Position 51-59 (Length 9)
            # @INFO: 7 enteros y 2 decimales sin coma
            r51_amount_total_cal = line.amount_currency + r51_amount_charge_cal
            r51_amount_total_raw = "%0.2f" % (r51_amount_total_cal,)
            r51_amount_total = r51_amount_total_raw.replace('.', '').zfill(9)

            # r54_rest - Position 16-82 (Length 67)
            # @INFO: fill the rest of R54 because we use only one subconcept
            r54_rest = str(' ' * 67)

            # r98_number_values - Position 3-10 (Length 8)
            r98_number_values = str(entry_num).zfill(8)

            # r98_amount_total - Position 11-22 (Length 12)
            # @INFO: (10 enteros y 2 decimales sin coma)
            r98_amount_charge = r98_amount_total_sum * \
                float(self.surcharge_percentage)
            r98_amount_total_cal = r98_amount_total_sum + r98_amount_charge
            r98_amount_total_raw = "%0.2f" % (r98_amount_total_sum,)
            r98_amount_total = r98_amount_total_raw.replace('.', '').zfill(12)

            # Generate filename (Tejaaavp.txt.)
            #  ej  -- son los dos últimos dígitos del año
            #  aaa -- es el código numérico de la agencia
            #  v   -- es el código del tipo de valor
            #  p   -  es un dígito del 0 al 9.
            periodicity = self.periodicity

            filename = 'T' + r51_year + r51_agency_code + r51_value_type + \
                periodicity + ".txt"

            # r98_filename - Position 32-42 (Length 11)
            r98_filename = filename.replace('.','')

            # r99_subconcept_code_01 - Position 3-5 (Length 3)
            r99_subconcept_code_01 = r54_concept_code

            # r99_num_val_01 - Position 6-12 (Length 7)
            r99_num_val_sub_01 = str(entry_num).zfill(7)

            # r99_amount_sub_01 - Position 13-22 (Length 10)
            r99_amount_sub_01 = r51_amount_total_raw.replace('.', '').zfill(10)

            # r99_rest - Position 23-82 (Length 60)
            # @INFO: Only one subconcept by file
            r99_rest = str(' ' * 60)

            # Log registre fields with length [and expected length]
            _log.info('NEW REGISTRE. Number %s ##############################'
                      % str(entry_num).zfill(2))
            _log.info('R51 r51_type                     (length %s [002]): %s'
                      % (str(len(r51_type)).zfill(3), r51_type))
            _log.info('R51 r51_year                     (length %s [002]): %s'
                      % (str(len(r51_year)).zfill(3), r51_year))
            _log.info('R51 r51_agency_code              (length %s [003]): %s'
                      % (str(len(r51_agency_code)).zfill(3), r51_agency_code))
            _log.info('R51 r51_income_type              (length %s [003]): %s'
                      % (str(len(r51_income_type)).zfill(3), r51_income_type))
            _log.info('R51 r51_value_type               (length %s [001]): %s'
                      % (str(len(r51_value_type)).zfill(3), r51_value_type))
            _log.info('R51 r51_issuing_ref              (length %s [007]): %s'
                      % (str(len(r51_issuing_ref)).zfill(3), r51_issuing_ref))
            _log.info('R51 r51_fixed_num                (length %s [020]): %s'
                      % (str(len(r51_fixed_num)).zfill(3), r51_fixed_num))
            _log.info('R51 r51_personality              (length %s [001]): %s'
                      % (str(len(r51_personality)).zfill(3), r51_personality))
            _log.info('R51 r51_vat                      (length %s [009]): %s'
                      % (str(len(r51_vat)).zfill(3), r51_vat))
            _log.info('R51 r51_subconcept_num           (length %s [002]): %s'
                      % (str(len(r51_subconcept_num)).zfill(3),
                         r51_subconcept_num))
            _log.info('R51 r51_amount_total             (length %s [009]): %s'
                      % (str(len(r51_amount_total)).zfill(3),
                         r51_amount_total))
            _log.info('R51 r51_amount_main              (length %s [009]): %s'
                      % (str(len(r51_amount_main)).zfill(3), r51_amount_main))
            _log.info('R51 r51_amount_charge            (length %s [008]): %s'
                      % (str(len(r51_amount_charge)).zfill(3),
                         r51_amount_charge))
            _log.info('R51 r51_notification_date        (length %s [006]): %s'
                      % (str(len(r51_notification_date)).zfill(3),
                         r51_notification_date))

            _log.info('R52 r52_type                     (length %s [002]): %s'
                      % (str(len(r52_type)).zfill(3), r52_type))
            _log.info('R52 r52_name                     (length %s [040]): %s'
                      % (str(len(r52_name)).zfill(3), r52_name))
            _log.info('R52 r52_street_type              (length %s [002]): %s'
                      % (str(len(r52_street_type)).zfill(3), r52_street_type))
            _log.info('R52 r52_address                  (length %s [038]): %s'
                      % (str(len(r52_address)).zfill(3), r52_address))

            _log.info('R53 r53_type                     (length %s [002]): %s'
                      % (str(len(r53_type)).zfill(3), r53_type))
            _log.info('R53 r53_ine_province             (length %s [002]): %s'
                      % (str(len(r53_ine_province)).zfill(3),
                         r53_ine_province))
            _log.info('R53 r53_ine_county               (length %s [003]): %s'
                      % (str(len(r53_ine_county)).zfill(3), r53_ine_county))
            _log.info('R53 r53_zip                      (length %s [005]): %s'
                      % (str(len(r53_zip)).zfill(3), r53_zip))
            _log.info('R53 r53_county                   (length %s [025]): %s'
                      % (str(len(r53_county)).zfill(3), r53_county))
            _log.info('R53 r53_tax_object               (length %s [045]): %s'
                      % (str(len(r53_tax_object)).zfill(3), r53_tax_object))

            _log.info('R54 r54_type                     (length %s [002]): %s'
                      % (str(len(r54_type)).zfill(3), r54_type))
            _log.info('R54 r54_concept_code             (length %s [003]): %s'
                      % (str(len(r54_concept_code)).zfill(3),
                         r54_concept_code))
            _log.info('R54 r54_amount                   (length %s [010]): %s'
                      % (str(len(r54_amount)).zfill(3), r54_amount))
            _log.info('R54 r54_rest                     (length %s [067]): %s'
                      % (str(len(r54_rest)).zfill(3), r54_rest))

            _log.info('R55 r55_type                     (length %s [002]): %s'
                      % (str(len(r55_type)).zfill(3), r55_type))
            _log.info('R55 r55_bank_code                (length %s [004]): %s'
                      % (str(len(r55_bank_code)).zfill(3), r55_bank_code))
            _log.info('R55 r55_bank_office_code         (length %s [004]): %s'
                      % (str(len(r55_bank_office_code)).zfill(3),
                         r55_bank_office_code))
            _log.info('R55 r55_bank_control_digit       (length %s [002]): %s'
                      % (str(len(r55_bank_control_digit)).zfill(3),
                         r55_bank_control_digit))
            _log.info('R55 r55_bank_acc_number          (length %s [010]): %s'
                      % (str(len(r55_bank_acc_number)).zfill(3),
                         r55_bank_acc_number))
            _log.info('R55 r55_bank_acc_holder          (length %s [040]): %s'
                      % (str(len(r55_bank_acc_holder)).zfill(3),
                         r55_bank_acc_holder))
            _log.info('R55 r55_bank_acc_holder_person   (length %s [001]): %s'
                      % (str(len(r55_bank_acc_holder_personality)).zfill(3),
                         r55_bank_acc_holder_personality))
            _log.info('R55 r55_bank_acc_holder_vat      (length %s [009]): %s'
                      % (str(len(r55_bank_acc_holder_vat)).zfill(3),
                         r55_bank_acc_holder_vat))
            _log.info('R55 r55_bank_rest                (length %s [010]): %s'
                      % (str(len(r55_bank_rest)).zfill(3), r55_bank_rest))

            _log.info('R66 r66_type                     (length %s [002]): %s'
                      % (str(len(r66_type)).zfill(3), r66_type))
            _log.info('R66 r66_content                  (length %s [080]): %s'
                      % (str(len(r66_content)).zfill(3), r66_content))

            _log.info('R98 r98_type                     (length %s [002]): %s'
                      % (str(len(r98_type)).zfill(3), r98_type))
            _log.info('R98 r98_number_values            (length %s [008]): %s'
                      % (str(len(r98_number_values)).zfill(3),
                         r98_number_values))
            _log.info('R98 r98_amount_total             (length %s [012]): %s'
                      % (str(len(r98_amount_total)).zfill(3),
                         r98_amount_total))
            _log.info('R98 r98_number_subconcepts       (length %s [003]): %s'
                      % (str(len(r98_number_subconcepts)).zfill(3),
                         r98_number_subconcepts))
            _log.info('R98 r98_generation_date          (length %s [006]): %s'
                      % (str(len(r98_generation_date)).zfill(3),
                         r98_generation_date))
            _log.info('R98 r98_filename                 (length %s [011]): %s'
                      % (str(len(r98_filename)).zfill(3), r98_filename))
            _log.info('R98 r98_rest                     (length %s [040]): %s'
                      % (str(len(r98_rest)).zfill(3), r98_rest))

            _log.info('R99 r99_type                     (length %s [002]): %s'
                      % (str(len(r99_type)).zfill(3), r99_type))
            _log.info('R99 r99_subconcept_code_01       (length %s [003]): %s'
                      % (str(len(r99_subconcept_code_01)).zfill(3),
                         r99_subconcept_code_01))
            _log.info('R99 r99_num_val_sub_01           (length %s [007]): %s'
                      % (str(len(r99_num_val_sub_01)).zfill(3),
                         r99_num_val_sub_01))
            _log.info('R99 r99_amount_sub_01            (length %s [010]): %s'
                      % (str(len(r99_amount_sub_01)).zfill(3),
                         r99_amount_sub_01))
            _log.info('R99 r99_rest                     (length %s [060]): %s'
                      % (str(len(r99_rest)).zfill(3), r99_rest))


            # Construct registres
            registre_51 = r51_type + r51_year + r51_agency_code + \
                r51_income_type + r51_value_type + r51_issuing_ref + \
                r51_fixed_num + r51_personality + r51_vat + \
                r51_subconcept_num + r51_amount_total + r51_amount_main + \
                r51_amount_charge + r51_notification_date + "\r\n"

            registre_52 = r52_type + r52_name + r52_street_type + \
                r52_address + "\r\n"

            registre_53 = r53_type + r53_ine_province + r53_ine_county + \
                r53_zip + r53_county + r53_tax_object + "\r\n"

            registre_54 = r54_type + r54_concept_code + r54_amount + \
                r54_rest + "\r\n"

            # registre_55 is done only if mandate_id exists

            registre_66 = r66_type + r66_content + "\r\n"

            registre_98 = r98_type + r98_number_values + r98_amount_total + \
                r98_number_subconcepts + r98_generation_date + r98_filename + \
                r98_rest + "\r\n"

            registre_99 = r99_type + r99_subconcept_code_01 + \
                r99_num_val_sub_01 + r99_amount_sub_01 + r99_rest + "\r\n"

            _log.info('FULL REGISTRE 51                 (length %s [082]): %s'
                      % (str(len(registre_51)).zfill(3), registre_51))
            _log.info('FULL REGISTRE 52                 (length %s [082]): %s'
                      % (str(len(registre_52)).zfill(3), registre_52))
            _log.info('FULL REGISTRE 53                 (length %s [082]): %s'
                      % (str(len(registre_53)).zfill(3), registre_53))
            _log.info('FULL REGISTRE 54                 (length %s [082]): %s'
                      % (str(len(registre_54)).zfill(3), registre_54))
            _log.info('FULL REGISTRE 55                 (length %s [082]): %s'
                      % (str(len(registre_55)).zfill(3), registre_55))
            _log.info('FULL REGISTRE 66                 (length %s [082]): %s'
                      % (str(len(registre_66)).zfill(3), registre_66))
            _log.info('FULL REGISTRE 98                 (length %s [082]): %s'
                      % (str(len(registre_98)).zfill(3), registre_98))
            _log.info('FULL REGISTRE 99                 (length %s [082]): %s'
                      % (str(len(registre_99)).zfill(3), registre_99))

            # Add loop registres to file
            payment_file_str_raw += registre_51 + registre_52 + registre_53 + \
                registre_54 + registre_55 + registre_66

        # Add summary registres to file
        payment_file_str_raw += registre_98 + registre_99
        payment_file_str = payment_file_str_raw.encode(self.ENCODING_NAME,
                                                       self.ENCODING_TYPE)

        # Fill error tab
        if self.error_mode == 'permissive':
            self.errors_found = errors

        return payment_file_str, filename


    @api.multi
    def action_done_cancel(self):
        for order in self:
            if order.payment_mode_id.name == 'OVRv':
                for bline in order.bank_line_ids:
                    invoice = self.env['account.invoice'].search([
                            ('number', '=', bline.communication)])
                    invoice.write({
                            'in_ovrv': False,
                            'ovrv_ref': False,
                        })
        return super(AccountPaymentOrder, self).action_done_cancel()
