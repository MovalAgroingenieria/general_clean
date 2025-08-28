# -*- coding: utf-8 -*-
# 2022 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from datetime import datetime
import calendar


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    entity_code = fields.Selection([
        ("13706", "13706 - Comunidad de Regantes Torre Abraham"),
        ("13720", "13720 - Comunidad de Regantes Santa Cruz de los Cáñamos"),
        ("17703", "17703 - Comunitat de Regants del Molí de Pals"),
        ("17704", "17704 - Comunitat de Regants de la Presa de Colomers")],
        string="Entity Code",
        help="This code identifies the entity that sends the delegated "
             "charge to 'Tax management. County Council (SIT-GTT)'.")

    @api.multi
    def set_entity_code_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'entity_code', self.entity_code)


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    sit_gtt_ref = fields.Char(
        string="Sit GTT reference",
        readonly=True,
        help="This number indicates the payment reference if it has "
             "been made by Sit GTT")

    sit_gtt_sent = fields.Boolean(
        string="Sit GTT done",
        readonly=True,
        help="Indicates whether this payment has already been added "
             "to a Sit GTT payment file")


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    ENCODING_NAME = '8859'
    ENCODING_TYPE = 'replace'
    MONTHS = {'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4, 'MAYO': 5,
              'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8, 'SEPTIEMBRE': 9,
              'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12}
    BIMONTHS = {'PRIMER BIMESTRE': (1, 2), 'SEGUNDO BIMESTRE': (3, 4),
                'TERCER BIMESTRE': (5, 6), 'CUARTO BIMESTRE': (7, 8),
                'QUINTO BIMESTRE': (9, 10), 'SEXTO BIMESTRE': (11, 12)}
    TRIMONTHS = {'PRIMER TRIMESTRE': (1, 3), 'SEGUNDO TRIMESTRE': (4, 6),
                 'TERCER TRIMESTRE': (7, 9), 'CUARTO TRIMESTRE': (10, 12)}
    FOURMONTHS = {'PRIMER CUATRIMESTRE': (1, 4),
                  'SEGUNDO CUATRIMESTRE': (5, 8),
                  'TERCER CUATRIMESTRE': (9, 12)}
    SIXMONTHS = {'PRIMER SEMESTRE': (1, 6), 'SEGUNDO SEMESTRE': (7, 12)}

    def _get_entity_config_sit_gtt(self):
        code = self.env['ir.values'].get_default(
            'account.config.settings', 'entity_code')
        if code:
            entity = dict(self.env['account.config.settings'].fields_get(
                allfields=['entity_code'])['entity_code']['selection'])[code]
        else:
            entity = "Unconfigured"
        return entity

    def _default_charge_year(self):
        current_year = str(fields.datetime.now().year)
        return current_year

    # Error mode
    error_mode = fields.Selection([
        ('strict', 'Strict'),
        ('permissive', 'Permissive')],
        string="Error mode",
        default="strict",
        help="Strict mode does not allow errors. The permissive mode allows "
             "but they are collected in the 'Errors' tab.'")

    # Errors tab
    errors_found = fields.Text(
        string='Errors',
        readonly=True)

    # Fields
    payment_mode_name = fields.Char(
        compute='_compute_payment_mode_name',
        string="Payment mode name")

    entity = fields.Char(
        string="Entity",
        default=_get_entity_config_sit_gtt,
        compute="_compute_entity",
        readonly=True,
        help="This code identifies the entity that sends the delegated "
             "charge to local state council.\nThis parameter is set in"
             " the accounting configuration")

    charge_type = fields.Selection([
        ('E', 'Executive'),
        ('V', 'Voluntary')],
        string="Charge type",
        default="E",
        help="Period in which debts should be managed")

    charge_year = fields.Selection([
        ('2019', '2019'),
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022'),
        ('2023', '2023'),
        ('2024', '2024'),
        ('2025', '2025'),
        ('2026', '2026'),
        ('2027', '2027'),
        ('2028', '2028'),
        ('2029', '2029')],
        string="Charge year",
        help="The year in which the charge is charged",
        default=_default_charge_year)

    concept = fields.Selection([
        ('CU', 'CU - Irrigation Quota')],
        string="Concept",
        help="Concept by which the settlement or receipt is made.\nIt will "
             "be applied to all transactions",
        default="CU")

    period = fields.Selection([
        ('ANUAL', 'ANUAL'),
        ('ENERO', 'ENERO'),
        ('FEBRERO', 'FEBRERO'),
        ('MARZO', 'MARZO'),
        ('ABRIL', 'ABRIL'),
        ('MAYO', 'MAYO'),
        ('JUNIO', 'JUNIO'),
        ('JULIO', 'JULIO'),
        ('AGOSTO', 'AGOSTO'),
        ('SEPTIEMBRE', 'SEPTIEMBRE'),
        ('OCTUBRE', 'OCTUBRE'),
        ('NOVIEMBRE', 'NOVIEMBRE'),
        ('DICIEMBRE', 'DICIEMBRE'),
        ('PRIMER BIMESTRE', 'PRIMER BIMESTRE'),
        ('SEGUNDO BIMESTRE', 'SEGUNDO BIMESTRE'),
        ('TERCER BIMESTRE', 'TERCER BIMESTRE'),
        ('CUARTO BIMESTRE', 'CUARTO BIMESTRE'),
        ('QUINTO BIMESTRE', 'QUINTO BIMESTRE'),
        ('SEXTO BIMESTRE', 'SEXTO BIMESTRE'),
        ('PRIMER TRIMESTRE', 'PRIMER TRIMESTRE'),
        ('SEGUNDO TRIMESTRE', 'SEGUNDO TRIMESTRE'),
        ('TERCER TRIMESTRE', 'TERCER TRIMESTRE'),
        ('CUARTO TRIMESTRE', 'CUARTO TRIMESTRE'),
        ('PRIMER CUATRIMESTRE', 'PRIMER CUATRIMESTRE'),
        ('SEGUNDO CUATRIMESTRE', 'SEGUNDO CUATRIMESTRE'),
        ('TERCER CUATRIMESTRE', 'TERCER CUATRIMESTRE'),
        ('PRIMER SEMESTRE', 'PRIMER SEMESTRE'),
        ('SEGUNDO SEMESTRE', 'SEGUNDO SEMESTRE'),
        ('SIN PERIODO', 'SIN PERIODO')],
        string="Period",
        default="ANUAL",
        help="Type of period settled.\nIt will be applied to all "
             "transactions")

    issue_number = fields.Selection([
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06')],
        string="Issue number",
        default="01",
        help="Indicates the number to add to the maximum existing issue in "
             "the DB for that year, sub-organization and concept.")

    approval_decree_date = fields.Date(
        string="Approval decree date",
        default=lambda self: fields.datetime.now(),
        help="The date on which the shipment was approved in Executive.")

    approval_decree_number = fields.Char(
        string="Approval decree number",
        size=30)

    value_type = fields.Selection([
        ('L', 'Liquidation'),
        ('R', 'Receipt')],
        string="Value type",
        default="L")

    period_start_date = fields.Date(
        string="Period start date")

    period_end_date = fields.Date(
        string="Period end date")

    tax_object = fields.Char(
        string="Tax Object",
        size=80,
        help="The tax object. Max 80 characters.")

    _sql_constraints = [
        ('length_tax_object', 'CHECK(LENGTH(tax_object) <= 80)',
         'The tax object must be at most 80 characters long.')
    ]

    # Methods
    @api.depends('payment_mode_id')
    def _compute_payment_mode_name(self):
        # @INFO: payment mode name SIT GTT (mandatory)
        for record in self:
            record.payment_mode_name = record.payment_mode_id.name

    # On change payment mode force date_prefered
    @api.onchange('payment_mode_name')
    def _onchange_payment_mode_name(self):
        if self.payment_mode_name == 'SIT GTT':
            self.date_prefered = 'due'

    # Set entity
    @api.depends('payment_mode_name')
    def _compute_entity(self):
        for record in self:
            record.entity = record._get_entity_config_sit_gtt()

    # Calculate period dates
    def _get_period_dates(self, period, charge_year):
        if period != 'SIN PERIODO':
            charge_year = int(charge_year)
            if period == 'ANUAL':
                period_start_date = datetime(charge_year, 1, 1)
                period_end_date = datetime(charge_year, 12, 31)
            elif period in self.MONTHS:
                month_num = MONTHS[period]
                period_start_date = datetime(charge_year, month_num, 1)
                last_month_day = calendar.monthrange(charge_year, month_num)[1]
                period_end_date = datetime(
                    charge_year, month_num, last_month_day)
            elif (period in self.BIMONTHS or period in self.TRIMONTHS or
                    period in self.FOURMONTHS or period in self.SIXMONTHS):
                if period in self.BIMONTHS:
                    start_month, end_month = self.BIMONTHS[period]
                elif period in self.TRIMONTHS:
                    start_month, end_month = self.TRIMONTHS[period]
                elif period in self.FOURMONTHS:
                    start_month, end_month = self.FOURMONTHS[period]
                elif period in self.SIXMONTHS:
                    start_month, end_month = self.SIXMONTHS[period]
                period_start_date = datetime(charge_year, start_month, 1)
                last_month_day = calendar.monthrange(charge_year, end_month)[1]
                period_end_date = datetime(
                    charge_year, end_month, last_month_day)
            period_start_date = period_start_date.strftime('%Y%m%d')
            period_end_date = period_end_date.strftime('%Y%m%d')
            return period_start_date, period_end_date

    # Generate payment file
    @api.multi
    def generate_payment_file(self):
        self.ensure_one()
        _log = logging.getLogger(self.__class__.__name__)
        pay_method = self.payment_method_id

        if pay_method.code != 'debit_sit_gtt':
            return super(AccountPaymentOrder, self).generate_payment_file()

        # Declare error vars
        self.errors_found = ""
        errors = ""
        error_num = 0

        # Charges file
        # Charge year - Position [001-004] Length 4
        charge_year = str(self.charge_year)

        # Entity code - Position [005-009] Length 5
        if self.entity == 'Unconfigured':
            raise ValidationError(
                _("The entity has not been configured. Set it "
                  "in Accounting/Settings."))
        else:
            entity_code = self.env['ir.values'].get_default(
                'account.config.settings', 'entity_code')

        # Charge concept code - Position [010-011] Length 2
        concept_code = self.concept

        # Issue number - Position [012-013] Length 2
        issue_number = self.issue_number

        # Value type - Position [014-014] Length 1
        value_type = self.value_type

        # Line format - Position [021-022] Length 2
        line_format = "DV"

        # Line format - Position [023-024] Length 2
        body_format = "LI"

        # Charge type - Position [025-025] Length 1
        charge_type = self.charge_type

        # Exercise - Position [026-029] Length 4
        # @INFO: In the loop

        # Period - Position [030-059] Length 30
        period = self.period.ljust(30)

        # Accrual date - Position [060-067] Length 8
        accrual_date = str('0' * 8)

        # Others non-changing params
        # Others address params - Position [225-262] Length 38
        street_num_duplicate = str(' ' * 5)
        street_num2 = str('0' * 5)
        street_num2_duplicate = str(' ' * 5)
        street_staircase = str(' ' * 2)
        street_floor = str(' ' * 3)
        street_door = str(' ' * 5)
        street_gate = str(' ' * 2)
        street_block = str(' ' * 4)
        street_km = str('0' * 5)
        street_hand = str(' ' * 2)
        street_other_params = street_num_duplicate + street_num2 + \
            street_num2_duplicate + street_staircase + street_floor + \
            street_door + street_gate + street_block + street_km + \
            street_hand
        # Local entity - Position [293-332] Length 40
        local_entity = str(' ' * 40)
        # County code - Position [368-372] Length 5
        county_code = str('0' * 5)
        # Tax object - Position [373-452] Length 80
        # @INFO: Mandatory on 18.08.2025.
        tax_object = self.tax_object.ljust(80)
        # Tax amount - Position [477-486] Length 10
        tax_amount = str('0' * 10)
        # Provincial surcharge amount - Position [487-496] Length 10
        prov_surch_amount = str('0' * 10)
        # Summrize tax not changing params 1 - Position [477-496] Length 20
        tax_other_params_1 = tax_amount + prov_surch_amount
        # Municipal fee - Position [497-506] Length 10
        # @INFO: Mandatory. In the loop. Equal to main_amount.
        # Section IAE - Position [507-507] Length 1
        section_iae = "0"
        # Canon amount - Position [508-517] Length 10
        canon_amount = str('0' * 10)
        # Gains bonus - Position [518-524] Length 7
        gains_bonus = str('0' * 7)
        # Untimely surcharge - Position [525-534] Length 10
        untimely_surcharge = str('0' * 10)
        # Untimely interest - Position [535-544] Length 10
        untimely_interest = str('0' * 10)
        # Summrize tax not changing params 2 - Position [507-544] Length 38
        tax_other_params_2 = section_iae + canon_amount + gains_bonus + \
            untimely_surcharge + untimely_interest
        # External ref - Position [545-573] Length 29
        # @INFO: In the loop.
        # Accounting ref - Position [574-593] Length 20
        accounting_ref = str(' ' * 20)
        # Cadastral ref - Position [594-613] Length 20
        cadastral_ref = str(' ' * 20)
        # Accounting ref - Position [614-617] Length 4
        accounting_year = str('0' * 4)
        # Summrize tax not changing params 3 - Position [574-617] Length 44
        tax_other_params_3 = accounting_ref + cadastral_ref + accounting_year
        # Approval decree date - Position [618-625] Length 8
        if charge_type == 'E':
            approval_decree_date = self.approval_decree_date.replace('-', '')
        elif charge_type == 'V':
            approval_decree_date = str('0' * 8)
        # Approval decree number - Position [626-655] Length 30
        if charge_type == 'E':
            approval_decree_number = self.approval_decree_number.ljust(30)
        elif charge_type == 'V':
            approval_decree_number = str(' ' * 30)
        # Voluntary start date - Position [656-663] Length 8
        voluntary_start_date = str('0' * 8)
        # LOPD - Position [672-679] Length 8
        lopd = str('0' * 8)
        # Notification date - Position [680-687] Length 8
        notification_date = str('0' * 8)
        # Notification result - Position [688-689] Length 2
        notification_result = str(' ' * 2)
        # Notification result - Position [690-719] Length 30
        notification_number = str(' ' * 30)
        # Notification sign date - Position [720-727] Length 8
        if charge_type == 'E':
            # @INFO: Equal to  approval_decree_date
            notification_sign_date = approval_decree_date
        elif charge_type == 'V':
            notification_sign_date = str('0' * 8)
        # Notification agency - Position [728-757] Length 30
        notification_agency = str(' ' * 30)
        # Notification voluntary date - Position [758-765] Length 8
        notification_vol_date = str('0' * 8)
        # Notification voluntary result - Position [766-767] Length 2
        notification_vol_result = str(' ' * 2)
        # Period start date - Position [768-775] Length 8
        # Period end date   - Position [776-783] Length 8
        if self.period != 'SIN PERIODO':
            period_start_date, period_end_date = self._get_period_dates(
                self.period, charge_year)
        else:
            period_start_date = self.period_start_date.replace('-', '')
            period_end_date = self.period_end_date.replace('-', '')
        # Dates description interruption - Position [784-1123] Lenght 340
        dates_interruption = (str('0' * 8) + str(' ' * 60)) * 5
        # Direct debit data - Position [1124-2040] Lenght 917
        direct_debit_data = str(' ' * 70) + str('0' * 8) + str(' ' * 47) + \
            str('0' * 8) + str(' ' * 784)
        # Summrize notification params - Position [672-2040] Length 1369
        notification_params = lopd + notification_date + \
            notification_result + notification_number + \
            notification_sign_date + notification_agency + \
            notification_vol_date + notification_vol_result + \
            period_start_date + period_end_date + dates_interruption + \
            direct_debit_data

        # Reset variables
        bank_lines = ""
        entry_num = 0

        # Iterate over bank lines
        for line in self.bank_line_ids:

            # Value number
            entry_num += 1
            entry_num_padded = str(entry_num).zfill(6)

            # Check if bank line is already done by sit_gtt
            if line.sit_gtt_sent:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, the bank line "
                          "%s seems that it has already been sent through "
                          "SIT GTT" % (entry_num_padded, line.name)) + '\n'
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, the bank line "
                          "%s seems that it has already been sent through "
                          "SIT GTT" % (entry_num_padded, line.name)))

            # Value list refnum - Position [015-020] Length 6
            # @INFO: Relation DV <--> LI
            #        This number is associate to each bank line
            value_list_refnum = self.env['ir.sequence'].next_by_code(
                'sit_gtt_seq_value_list_refnum')

            # VAT - Position [068-077] Length 10
            # @INFO: The two first chars are sliced
            if line.partner_id.vat:
                taxpayer_vat = line.partner_id.vat[2:]
                if len(taxpayer_vat) > 9 or not \
                        line.partner_id.vat[3:-1].isdigit():
                    if self.error_mode == 'permissive':
                        error_num += 1
                        errors += '[' + str(error_num).zfill(4) + '] ' + \
                            _("The entry number %s has failed, the vat %s "
                              "for partner %s is not valid." %
                              (entry_num_padded, taxpayer_vat,
                               line.partner_id.name)) + '\n'
                        taxpayer_vat = str(taxpayer_vat).ljust(10)
                    else:
                        raise ValidationError(
                            _("The entry number %s has failed, the vat %s "
                              "for partner %s is not valid." %
                              (entry_num_padded, taxpayer_vat,
                               line.partner_id.name)))
                taxpayer_vat = str(taxpayer_vat).ljust(10)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, vat not found "
                          "for partner %s." % (entry_num_padded,
                                               line.partner_id.name)) + '\n'
                    taxpayer_vat = str(" " * 10)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, vat not found "
                          "for partner %s." % (entry_num_padded,
                                               line.partner_id.name)))

            # Taxpayer name - Position [078-137] Length 60
            # @INFO: lastname1 lastname2, firstname
            if line.partner_id.company_type == 'company':
                # @INFO: delete points and replace commas by spaces
                #        Limit and justify to 60 chars
                taxpayer_name = \
                    line.partner_id.name.replace(
                        ".", "").replace(",", " ")[:60].upper()
                taxpayer_name_padded = taxpayer_name.ljust(60)
            elif line.partner_id.company_type == 'person':
                # @INFO: partner_second_lastname dependence
                if line.partner_id.lastname:
                    taxpayer_name = line.partner_id.lastname.upper()
                    if line.partner_id.lastname2:
                        taxpayer_name += ' ' + \
                            line.partner_id.lastname2.upper()
                else:
                    if self.error_mode == 'permissive':
                        error_num += 1
                        errors += '[' + str(error_num).zfill(4) + '] ' + \
                            _("The entry number %s has failed, the lastname"
                              "for partner %s not found." %
                              (entry_num_padded, line.partner_id.name)) + '\n'
                    else:
                        raise ValidationError(
                            _("The entry number %s has failed, the lastname"
                              "for partner %s not found." %
                              (entry_num_padded, line.partner_id.name)))
                if line.partner_id.firstname:
                    taxpayer_name += ' ' + line.partner_id.firstname.upper()
                else:
                    if self.error_mode == 'permissive':
                        error_num += 1
                        errors += '[' + str(error_num).zfill(4) + '] ' + \
                            _("The entry number %s has failed, the firstname "
                              "for partner %s not found." %
                              (entry_num_padded, line.partner_id.name)) + '\n'
                    else:
                        raise ValidationError(
                            _("The entry number %s has failed, the firstname "
                              "for partner %s not found." %
                              (entry_num_padded, line.partner_id.name)))
                taxpayer_name_padded = taxpayer_name.ljust(60)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, taxpayer name not "
                          "found." % (entry_num_padded)) + '\n'
                    taxpayer_name_padded = str(" " * 60)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, taxpayer name not "
                          "found." % (entry_num_padded)))

            # Taxpayer address - Position [138-367] Length 230
            # Street type - Position [138-139] Length 2
            if line.partner_id.street_type_id:
                taxpayer_address_street_type = \
                    line.partner_id.street_type_id.abbreviation
            else:
                taxpayer_address_street_type = "CL"

            # Street name - Position [140-179] Length 40
            if line.partner_id.street:
                taxpayer_address_street_name = \
                    line.partner_id.street[:40].upper().ljust(40)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, taxpayer "
                          "street not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)) + \
                        '\n'
                    taxpayer_address_street_name = str(" " * 40)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, taxpayer "
                          "street not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)))

            # Street name extension - Position [180-219] Length 40
            if line.partner_id.street2:
                taxpayer_address_street_name_ext = \
                    line.partner_id.street2[:40].upper().ljust(40)
            else:
                taxpayer_address_street_name_ext = str(' ' * 40)

            # Street number - Position [220-224] Length 5
            if line.partner_id.street_num:
                taxpayer_address_street_number = \
                    filter(lambda x: x.isdigit(),
                           line.partner_id.street_num)
                taxpayer_address_street_number = \
                    str(taxpayer_address_street_number).zfill(5)
            else:
                taxpayer_address_street_number = str(" " * 5)

            # Others address params - Position [225-262] Length 38
            # @INFO: Outside the loop

            # City - Position [263-292] Length 30
            if line.partner_id.city:
                city_name = ""

                if '(' in line.partner_id.city:
                    # Get name between parenthesis
                    city_name = line.partner_id.city.split('(')[0]
                elif '/' in line.partner_id.city:
                    # Get name before bar
                    city_name = line.partner_id.city.split('/')[0]
                else:
                    city_name = line.partner_id.city
                city = city_name[:30].upper().ljust(30)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, debtor city "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)) + '\n'
                    city = str(" " * 30)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, debtor city "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)))

            # Local entity - Position [293-332] Length 40
            # @INFO: Outside the loop

            # Province - Position [333-362] Length 30
            if line.partner_id.state_id:
                province = line.partner_id.state_id.name[:30].upper().ljust(30)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, debtor state "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)) + '\n'
                    province = str(" " * 30)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, debtor state "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)))

            # ZIP code - Position [363-367] Length 5
            if line.partner_id.zip:
                city_zip = str(line.partner_id.zip)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, taxpayer zip "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)) + '\n'
                    city_zip = str(" " * 5)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, taxpayer zip "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)))

            # County code - Position [368-372] Length 5
            # @INFO: Outside the loop

            # Tax object - Position [373-452] Length 80
            # @INFO: Mandatory on 18.08.2025. Outside the loop

            # Fixed number - Position [453-466] Length 14
            # @INFO: Mandatory on 18.08.2025. Using partner_code
            if line.partner_id.partner_code:
                partner_code_str = str(line.partner_id.partner_code)
                fixed_number = partner_code_str.ljust(14)
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, fixed number "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)) + '\n'
                    fixed_number = str(" " * 14)
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, fixed number "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)))

            # Main amount - Position [467-476] Length 10
            # @INFO: In euro cents with two decimals
            if line.amount_currency:
                amount_cents = int(line.amount_currency * 100)
                main_amount = str(amount_cents).zfill(10)
                municipal_fee = main_amount
            else:
                if self.error_mode == 'permissive':
                    error_num += 1
                    errors += '[' + str(error_num).zfill(4) + '] ' + \
                        _("The entry number %s has failed, amount "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)) + \
                        '\n'
                    main_amount = str('0' * 10)
                    municipal_fee = main_amount
                else:
                    raise ValidationError(
                        _("The entry number %s has failed, amount "
                          "not found for partner %s" %
                          (entry_num_padded, line.partner_id.name)))

            # Summrize tax not changing params - Position [477-617] Length 141
            # @INFO: Outside the loop
            # Approval decree date - Position [618-625] Length 8
            # @INFO: Outside the loop
            # Approval decree number - Position [626-655] Length 30
            # @INFO: Outside the loop
            # Voluntary start date - Position [656-663] Length 8
            # @INFO: Outside the loop

            # Voluntary end date - Position [664-671] Length 8
            # @INFO: Mandatory if Executive charge type
            voluntary_end_date = False
            exercise = False
            external_ref = str(' ' * 29)
            invoice = False
            if line.payment_line_ids:
                for l in line.payment_line_ids:
                    if line.name == l.bank_line_id.name:
                        voluntary_end_date = \
                            l.ml_maturity_date.replace('-', '')
                        # Exercise - Position [026-029] Length 4
                        if l.invoice_id:
                            exercise = l.invoice_id.date_invoice.split('-')[0]
                            external_ref = l.invoice_id.number.ljust(29)
                            invoice = l.invoice_id
            if charge_type == 'E':
                if not voluntary_end_date or not exercise:
                    if self.error_mode == 'permissive':
                        error_num += 1
                        errors += '[' + str(error_num).zfill(4) + '] ' + \
                            _("The entry number %s has failed, voluntary end "
                              "date or exercise not found for partner %s" %
                              (entry_num_padded, line.partner_id.name)) + '\n'
                        voluntary_end_date = str('0' * 8)
                        exercise = str('0' * 4)
                    else:
                        raise ValidationError(
                            _("The entry number %s has failed, voluntary end "
                              "date or exercise not found for partner %s" %
                              (entry_num_padded, line.partner_id.name)))
            elif charge_type == 'V':
                voluntary_end_date = str('0' * 8)
                if not exercise:
                    if self.error_mode == 'permissive':
                        error_num += 1
                        errors += '[' + str(error_num).zfill(4) + '] ' + \
                            _("The entry number %s has failed, exercise "
                              "not found for partner %s" %
                              (entry_num_padded, line.partner_id.name)) + '\n'
                        exercise = str('0' * 4)
                    else:
                        raise ValidationError(
                            _("The entry number %s has failed, exercise "
                              "not found for partner %s" %
                              (entry_num_padded, line.partner_id.name)))

            # Summrize notification params - Position [672-2040] Length 1369
            # @INFO: Outside the loop

            # Log bank line fields with length [and expected length]
            _log.info('NEW BANK LINE. Number %s #########################'
                      % str(entry_num).zfill(5))
            _log.info('BANK LINE FIELD Charge year      (length %s [0004]): %s'
                      % (str(len(charge_year)).zfill(4), charge_year))
            _log.info('BANK LINE FIELD Entity code      (length %s [0005]): %s'
                      % (str(len(entity_code)).zfill(4), entity_code))
            _log.info('BANK LINE FIELD Concept code     (length %s [0002]): %s'
                      % (str(len(concept_code)).zfill(4), concept_code))
            _log.info('BANK LINE FIELD Issue number     (length %s [0002]): %s'
                      % (str(len(issue_number)).zfill(4), issue_number))
            _log.info('BANK LINE FIELD Value type       (length %s [0001]): %s'
                      % (str(len(value_type)).zfill(4), value_type))
            _log.info('BANK LINE FIELD Value refnum     (length %s [0006]): %s'
                      % (str(len(value_list_refnum)).zfill(4),
                         value_list_refnum))
            _log.info('BANK LINE FIELD Line format      (length %s [0002]): %s'
                      % (str(len(line_format)).zfill(4), line_format))
            _log.info('BANK LINE FIELD Body format      (length %s [0002]): %s'
                      % (str(len(body_format)).zfill(4), body_format))
            _log.info('BANK LINE FIELD Charge type      (length %s [0001]): %s'
                      % (str(len(charge_type)).zfill(4), charge_type))
            _log.info('BANK LINE FIELD Exercise         (length %s [0004]): %s'
                      % (str(len(exercise)).zfill(4), exercise))
            _log.info('BANK LINE FIELD Period           (length %s [0030]): %s'
                      % (str(len(period)).zfill(4), period))
            _log.info('BANK LINE FIELD Accrual date     (length %s [0008]): %s'
                      % (str(len(accrual_date)).zfill(4), accrual_date))
            _log.info('BANK LINE FIELD VAT              (length %s [0010]): %s'
                      % (str(len(taxpayer_vat)).zfill(4), taxpayer_vat))
            _log.info('BANK LINE FIELD Taxpayer name    (length %s [0060]): %s'
                      % (str(len(taxpayer_name_padded)).zfill(4),
                         taxpayer_name_padded))
            _log.info('BANK LINE FIELD Street type      (length %s [0002]): %s'
                      % (str(len(taxpayer_address_street_type)).zfill(4),
                         taxpayer_address_street_type))
            _log.info('BANK LINE FIELD Street name      (length %s [0040]): %s'
                      % (str(len(taxpayer_address_street_name)).zfill(4),
                         taxpayer_address_street_name))
            _log.info('BANK LINE FIELD Street name ext  (length %s [0040]): %s'
                      % (str(len(taxpayer_address_street_name_ext)).zfill(4),
                         taxpayer_address_street_name_ext))
            _log.info('BANK LINE FIELD Street number    (length %s [0005]): %s'
                      % (str(len(taxpayer_address_street_number)).zfill(4),
                         taxpayer_address_street_number))
            _log.info('BANK LINE FIELD Street params    (length %s [0038]): %s'
                      % (str(len(street_other_params)).zfill(4),
                         street_other_params))
            _log.info('BANK LINE FIELD City             (length %s [0030]): %s'
                      % (str(len(city)).zfill(4), city))
            _log.info('BANK LINE FIELD Local entity     (length %s [0040]): %s'
                      % (str(len(local_entity)).zfill(4), local_entity))
            _log.info('BANK LINE FIELD Province         (length %s [0030]): %s'
                      % (str(len(province)).zfill(4), province))
            _log.info('BANK LINE FIELD City zip         (length %s [0005]): %s'
                      % (str(len(city_zip)).zfill(4), city_zip))
            _log.info('BANK LINE FIELD County code      (length %s [0005]): %s'
                      % (str(len(county_code)).zfill(4), county_code))
            _log.info('BANK LINE FIELD Tax_object       (length %s [0080]): %s'
                      % (str(len(tax_object)).zfill(4), tax_object))
            _log.info('BANK LINE FIELD Fixed number     (length %s [0014]): %s'
                      % (str(len(fixed_number)).zfill(4), fixed_number))
            _log.info('BANK LINE FIELD Main amount      (length %s [0010]): %s'
                      % (str(len(main_amount)).zfill(4), main_amount))
            _log.info('BANK LINE FIELD Tax params 1     (length %s [0020]): %s'
                      % (str(len(tax_other_params_1)).zfill(4),
                         tax_other_params_1))
            _log.info('BANK LINE FIELD Municipal_fee    (length %s [0010]): %s'
                      % (str(len(municipal_fee)).zfill(4),
                         municipal_fee))
            _log.info('BANK LINE FIELD Tax params 2     (length %s [0038]): %s'
                      % (str(len(tax_other_params_2)).zfill(4),
                         tax_other_params_2))
            _log.info('BANK LINE FIELD External ref     (length %s [0029]): %s'
                      % (str(len(external_ref)).zfill(4), external_ref))
            _log.info('BANK LINE FIELD Tax params 3     (length %s [0044]): %s'
                      % (str(len(tax_other_params_3)).zfill(4),
                         tax_other_params_3))
            _log.info('BANK LINE FIELD Approval date    (length %s [0008]): %s'
                      % (str(len(approval_decree_date)).zfill(4),
                         approval_decree_date))
            _log.info('BANK LINE FIELD Approval number  (length %s [0030]): %s'
                      % (str(len(approval_decree_number)).zfill(4),
                         approval_decree_number))
            _log.info('BANK LINE FIELD Vol. start date  (length %s [0008]): %s'
                      % (str(len(voluntary_start_date)).zfill(4),
                         voluntary_start_date))
            _log.info('BANK LINE FIELD Vol. end date    (length %s [0008]): %s'
                      % (str(len(voluntary_end_date)).zfill(4),
                         voluntary_end_date))
            _log.info('BANK LINE FIELD Notif params     (length %s [1369]): %s'
                      % (str(len(notification_params)).zfill(4),
                         notification_params))

            # Construct DV bank line
            dv_bank_line = charge_year + entity_code + concept_code + \
                issue_number + value_type + value_list_refnum + line_format + \
                body_format + charge_type + exercise + period + accrual_date +\
                taxpayer_vat + taxpayer_name_padded + \
                taxpayer_address_street_type + taxpayer_address_street_name + \
                taxpayer_address_street_name_ext + \
                taxpayer_address_street_number + street_other_params + city + \
                local_entity + province + city_zip + county_code + \
                tax_object + fixed_number + main_amount + tax_other_params_1 +\
                municipal_fee + tax_other_params_2 + external_ref + \
                tax_other_params_3 + approval_decree_date + \
                approval_decree_number + voluntary_start_date + \
                voluntary_end_date + notification_params + '\r\n'

            _log.info('FULL DV BANK LINE                (length %s [2040]): %s'
                      % (str(len(dv_bank_line)).zfill(4), dv_bank_line))

            # Add to DV bank_lines
            bank_lines += dv_bank_line

            # Detail lines (hook) - Position [25-1224] - Length 1200
            # @INFO: 15 lines * 80 characters
            lines_details = self.create_details_lines(
                self.description, line, invoice)

            _log.info('LI LINE FIELD Detail lines       (length %s [1200]): %s'
                      % (str(len(lines_details)).zfill(4), lines_details))

            # Create LI bank_lines
            li_bank_line = charge_year + entity_code + concept_code + \
                issue_number + value_type + value_list_refnum + body_format + \
                str(' ' * 2) + lines_details + str(' ' * 816) + '\r\n'

            _log.info('FULL LI BANK LINE                (length %s [2040]): %s'
                      % (str(len(li_bank_line)).zfill(4), li_bank_line))

            # Add to LI bank_lines
            bank_lines += li_bank_line

            # Set as done and add SIT GTT list ref
            line.write({
                'sit_gtt_ref': value_list_refnum,
                'sit_gtt_sent': True,
                })

        # Fill error tab
        if self.error_mode == 'permissive':
            self.errors_found = \
                _("Errors in payment file ") + "[" + str(error_num) \
                + " errors]\n" + errors

        # Send to the file and encode
        payment_file_str = bank_lines.encode(
            self.ENCODING_NAME, self.ENCODING_TYPE)

        # Generate filename
        filename = datetime.today().strftime("%Y%m%d") + '_' + body_format + \
            '_' + self.charge_type + '_' + self.name + ".txt"

        return payment_file_str, filename

    # Hooks (defaults)
    def get_entity_type_code(self):
        if self.entity_type_code:
            entity_type_code = self.entity_type_code
        else:
            raise ValidationError(_("Entity type code not set"))
        return entity_type_code

    def create_details_lines(self, description, line, invoice):
        # Detail line 1 - Position [25-105] Length 80
        if description:
            line_detail_1 = description[:80].ljust(80)
        else:
            line_detail_1 = str(" " * 80)
        # Detail line 2 - Position [106-185] Length 80
        # Detail line 3 - Position [186-255] Length 80
        for l in line.payment_line_ids:
            if line.name == l.bank_line_id.name:
                try:
                    invoice = l.invoice_id
                except not invoice:
                    invoice = False
        # Detail line 2
        if invoice:
            num = invoice.number
            # qty = invoice.quantity (invoice.line)
            invoice_amount = invoice.residual
            line_detail_2 = _("Invoice num: ") + num + ' ' + \
                _("Amount: ") + str(invoice_amount) + ' ' + \
                invoice.currency_id.name
            line_detail_2 = line_detail_2[:80].ljust(80)
            # Detail line 3
            quantity = 0.0
            if invoice.invoice_line_ids:
                unit = \
                    invoice.invoice_line_ids[00].uom_id.display_name or ""
                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.quantity:
                        quantity += invoice_line.quantity
                line_detail_3 = _("Quantity: ") + str(quantity) + ' ' + unit
                line_detail_3 = line_detail_3[:80].ljust(80)
        else:
            line_detail_2 = str(" " * 80)
            line_detail_3 = str(" " * 80)
        # Detail line 4-15 - Position [256-1225] Length 960
        line_detail_4_15 = str(" " * 80) * 12
        lines_details = line_detail_1 + line_detail_2 + line_detail_3 + \
            line_detail_4_15
        return lines_details

    # This method is replicated by wua_account_banking_debit_sit_gtt
    @api.multi
    def generated2uploaded(self):
        res = super(AccountPaymentOrder, self).generated2uploaded()
        for order in self:
            if order.payment_mode_id.name == 'SIT GTT':
                for bline in order.bank_line_ids:
                    if bline.sit_gtt_sent:
                        for l in bline.payment_line_ids:
                            if bline.name == l.bank_line_id.name:
                                invoice = l.invoice_id
                                invoice.write({
                                    'in_sit_gtt': True,
                                    'sit_gtt_ref': bline.sit_gtt_ref,
                                })
        return res

    @api.multi
    def action_done_cancel(self):
        for order in self:
            if order.payment_mode_id.name == 'SIT GTT':
                for bline in order.bank_line_ids:
                    for l in bline.payment_line_ids:
                        if bline.name == l.bank_line_id.name:
                            invoice = l.invoice_id
                            invoice.write({
                                'in_sit_gtt': False,
                                'sit_gtt_ref': False,
                                })
        return super(AccountPaymentOrder, self).action_done_cancel()
