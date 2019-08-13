# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
import logging
import unicodedata
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    agency_code = fields.Selection([
        ('001', '001 - ABANILLA'),
        ('002', '002 - ABARAN'),
        ('003', '003 - AGUILAS'),
        ('004', '004 - ALBUDEITE'),
        ('005', '005 - ALCANTARILLA'),
        ('006', '006 - ALEDO'),
        ('007', '007 - ALGUAZAS'),
        ('008', '008 - ALHAMA DE MURCIA'),
        ('009', '009 - ARCHENA '),
        ('010', '010 - BENIEL'),
        ('011', '011 - BLANCA'),
        ('012', '012 - BULLAS'),
        ('013', '013 - CALASPARRA'),
        ('014', '014 - CAMPOS DEL RIO '),
        ('015', '015 - CARAVACA DE LA CRUZ'),
        ('016', '016 - CARTAGENA'),
        ('017', '017 - CEHEGIN'),
        ('018', '018 - CEUTI'),
        ('019', '019 - CIEZA '),
        ('020', '020 - FORTUNA'),
        ('021', '021 - FUENTE ALAMO '),
        ('022', '022 - JUMILLA'),
        ('023', '023 - LIBRILLA '),
        ('024', '024 - LORCA'),
        ('025', '025 - LORQUI '),
        ('026', '026 - MAZARRON '),
        ('027', '027 - MOLINA DE SEGURA '),
        ('028', '028 - MORATALLA'),
        ('029', '029 - MULA'),
        ('030', '030 - MURCIA '),
        ('031', '031 - OJOS '),
        ('032', '032 - PLIEGO '),
        ('033', '033 - PUERTO-LUMBRERAS '),
        ('034', '034 - RICOTE'),
        ('035', '035 - SAN JAVIER'),
        ('036', '036 - SAN PEDRO DEL PINATAR'),
        ('037', '037 - TORRE-PACHECO'),
        ('038', '038 - LAS TORRES DE COTILLAS'),
        ('039', '039 - TOTANA'),
        ('040', '040 - ULEA'),
        ('041', '041 - UNION (LA)'),
        ('042', '042 - VILLANUEVA DEL RIO SEGURA'),
        ('043', '043 - YECLA'),
        ('044', '044 - SANTOMERA'),
        ('045', '045 - LOS ALCAZARES'),
        ('073', '073 - COMUNIDAD AUTÓNOMA REGIÓN DE MURCIA'),
        ('100', '100 - SERVICIO MURCIANO DE SALUD '),
        ('101', '101 - INSTITUTO DE FOMENTO'),
        ('102', '102 - CONSORCIO GESTION RESIDUOS SOLIDOS'),
        ('103', '103 - MANCOMUNIDAD MUNICIPIOS VALLE RICOTE'),
        ('104', '104 - CONSORCIO EXT.INCEND.Y SALVAM.DE LA CARM'),
        ('105', '105 - CMDAD.REGANTES HEREDAM.AGUAS DE ALGUAZAS'),
        ('106', '106 - COMUNIDAD DE REGANTES LAS TOSQUILLAS'),
        ('107', '107 - CMDAD.REGANTES POZO ROMAN NOSTRUM No3'),
        ('105', '105 - CMDAD.REGANTES HEREDAM.AGUAS DE ALGUAZAS'),
        ('106', '106 - COMUNIDAD DE REGANTES LAS TOSQUILLAS'),
        ('107', '107 - CMDAD.REGANTES POZO ROMAN NOSTRUM No3'),
        ('108', '108 - CMDAD.REGAN.PUENTE DEL CALDO Y MIRAVETES'),
        ('109', '109 - CMDAD.REGANTES MINAS Y SANTA INES'),
        ('110', '110 - MANCOMUNIDAD SERVIC.TURISTICOS NORDESTE'),
        ('111', '111 - HEREDAMIENTO REGANTE DE MOLINA DE SEGURA'),
        ('112', '112 - TRIBUNAL ECONOMICO ADMVO.REGIONAL(TEAR)'),
        ('113', '113 - MANCOMUNIDAD COMARCA ORIENTAL'),
        ('114', '114 - JUNTA HACENDADOS DE LA HUERTA DE MURCIA'),
        ('115', '115 - CMDAD.REGANTES NTRA.SRA.DE LA ESPERANZA'),
        ('116', '116 - CMDAD.REGANTES FUENTES DEL MARQUES'),
        ('117', '117 - CMDAD.REGANTES ZONA V SECTORES I Y II'),
        ('118', '118 - CMDAD.REGANTES POZO SAN MANUEL'),
        ('119', '119 - CONSORCIO TURISTICO DESFILADERO DE ALMAD'),
        ('120', '120 - CMDAD.REGANTES AGUAS REGULADAS EMB.ARGOS'),
        ('121', '121 - CMDAD.REGANTES HUERTA ALTA-PLIEGO'),
        ('122', '122 - CMDAD.REGANTES EL CAMPILLO'),
        ('123', '123 - CMDAD.REGANTES POZO SAN JOSE'),
        ('124', '124 - CMDAD.REGANTES ACEQUIA DE ARCHENA'),
        ('125', '125 - CMDAD.REGANTES FUENTE DE LA COPA'),
        ('200', '200 - CARM - ORGANISMO PAGADOR AGRICULTURA'),
        ('201', '201 - ENTE PUBLICO AGUA'),
        ('300', '300 - AGENCIA TRIBUTARIA REGION DE MURCIA'),
        ('501', '501 - GISCARMSA'),
        ('502', '502 - INSTITUTO TURISMO DE LA REGION DE MURCIA'),
        ('503', '503 - CONSEJO ECONOMICO Y SOCIAL REGION MURCIA'),
        ('504', '504 - INSTITUTO CREDITO Y FINANZAS REGION MURCIA'),
        ('505', '505 - ENTIDAD PUBLICA DEL TRANSPORTE'),
        ('506', '506 - INDUSTRIALHAMA, S.A.'),
        ('507', '507 - INST.MURCIANO INV.Y DESAR.AGRAR.Y ALIMEN'),
        ('508', '508 - SOC.PUB.SUELO EQUIP.EMPRESAR.REG.MURCIA'),
        ('509', '509 - BOLETIN OFICIAL DE LA REGION DE MURCIA'),
        ('700', '700 - AGENCIA ESTATAL ADMINISTRACION TRIBUTARIA'),
        ('703', '703 - OF.LIQ. DE AGUILAS'),
        ('715', '715 - OF.LIQ. DE CARAVACA'),
        ('716', '716 - ASAMBLEA REGIONAL'),
        ('717', '717 - ESAMUR'),
        ('719', '719 - OF.LIQ. DE CIEZA'),
        ('724', '724 - OF.LIQ. DE LORCA'),
        ('726', '726 - OF.LIQ. DE MAZARRON'),
        ('727', '727 - OF.LIQ. DE MOLINA SEGURA'),
        ('729', '729 - OF.LIQ. DE MULA'),
        ('735', '735 - OF.LIQ. DE SAN JAVIER'),
        ('739', '739 - OF.LIQ. DE TOTANA'),
        ('741', '741 - OF.LIQ. DE LA UNION'),
        ('743', '743 - OF.LIQ. DE YECLA'),
        ('794', '794 - INSTITUTO DE TURISMO DE LA REGION MURCIA'),
        ('795', '795 - INSTITUTO DE LA VIVIENDA Y SUELO'),
        ('796', '796 - INSTITUTO SEGURIDAD Y SALUD LABORAL CARM'),
        ('797', '797 - INSTITUTO JUVENTUD REGION MURCIA'),
        ('798', '798 - SERVICIO DE EMPLEO Y FORMACION'),
        ('799', '799 - IMAS'),
        ('900', '900 - MURCIA')],
        string="Agency Code",
        help="This code identifies the agency or municipality that sends\
            the delegated charge to ATRM.")

    agency_max_amount = fields.Float(
        string="Amount max",
        default=10000.0,
        help="Maximum amount allowed by the agency agreement.")

    agency_min_amount = fields.Float(
        string="Amount min",
        default=0.0,
        help="Minimum amount allowed by the agency agreement.")

    @api.multi
    def set_agency_code_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'agency_code', self.agency_code)

    @api.multi
    def set_agency_max_amount_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'agency_max_amount',
            self.agency_max_amount)

    @api.multi
    def set_agency_min_amount_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'agency_min_amount',
            self.agency_min_amount)


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    atrm_ref = fields.Char(
        string="ATRM reference",
        readonly=True,
        help="This number indicates the payment reference\
            if it has been made by ATRM.")

    atrm_sent = fields.Boolean(
        string="ATRM done",
        readonly=True,
        help="Indicates whether this payment has already been\
            added to an ATRM payment file.")


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    CONCEPT_CODES_NOT_ALLOWED = ('001', '003', '005', '006', '007', '018',
                                 '083')

    def _get_agency_config_atrm(self):
        code = self.env['ir.values'].get_default('account.config.settings',
                                                 'agency_code')
        if code:
            agency = dict(self.env['account.config.settings'].fields_get(
                allfields=['agency_code'])['agency_code']['selection'])[code]
        else:
            agency = "Unconfigured"
        return agency

    # Field just to show selected agency in account.config.settings
    payment_mode_name = fields.Char(
        compute='_compute_payment_mode_name',
        string="Payment mode name")

    # Field to choose registry type
    # @INFO: At the moment only Liquidation is programmed.
    registry_type = fields.Selection([
        ('1', 'Liquidation'),
        ('2', 'Executive notification'),
        ('3', 'Guarantees')],
        string="Registry type",
        readonly=True,
        default="1",
        help='This is the type of registry sent: Liquidation, Executive\
            notification or Guarantees.\nAt this time only the Liquidation\
            type is possible.')

    # Header fields
    shipment_num = fields.Char(
        string='Shipment number', size=9,
        default=lambda self: self._get_next_shipment_num(),
        readonly=True,
        help='Year and shipment number. Format YYYYNNNNN. Self generated.')

    agency = fields.Char(
        string="Agency",
        default=_get_agency_config_atrm,
        compute="_compute_agency",
        readonly=True,
        help="This code identifies the agency or municipality that sends\
            the delegated charge to ATRM.\nThis parameter is set in the\
            accounting configuration.")

    shipment_date = fields.Date(
        string='Shipment date',
        default=datetime.today())

    debt_period = fields.Selection([
        ('V', 'Volunteer'),
        ('E', 'Executive'),
        ('B', 'Embargo')],
        string="Debt period",
        help="Period in which debts should be managed.", default="V")

    # Line fields
    concept_code = fields.Selection([
        ('001', '001 - RB - IMPUESTO SOBRE BIENES INMUEBLES DE NATURALEZA\
        URBANA'),
        ('002', '002 - RB - IMPUESTO SOBRE BIENES INMUEBLES DE NATURALEZA\
        RUSTICA'),
        ('003', '003 - LQ - LIQUIDACION IBI URBANA'),
        ('004', '004 - LQ - LIQUIDACION IBI RUSTICA'),
        ('005', '005 - RB - I.S/ACTIVIDADES ECONOMICAS'),
        ('006', '006 - LQ - LIQUIDACION DEL IMPUESTO SOBRE ACTIVIDADES\
        ECONOMICAS'),
        ('007', '007 - RB - I. VEHICULOS TRACCION MECANICA'),
        ('008', '008 - LQ - IMPUESTO CONTR.INSTAL. Y OBRAS'),
        ('009', '009 - LQ - INCRE.VALOR TERRENOS (PLUSVALIA)'),
        ('010', '010 - RB - CONT. URBANA'),
        ('011', '011 - LQ - LIQ. CONT. URBANA'),
        ('012', '012 - RB - CONT. RUSTICA'),
        ('013', '013 - LQ - LIQ. CONT. RUSTICA'),
        ('014', '014 - RB - CONT. RUST.- GANADERIA'),
        ('015', '015 - RB - L.F. INDUSTRIAL'),
        ('016', '016 - RB - L.F. PROFESIONAL'),
        ('017', '017 - RB - CIRC. VEHICULOS TRAC.MECANICA'),
        ('018', '018 - LQ - IMPUESTO INCREMENTO VALOR TERRENOS URBANOS'),
        ('019', '019 - RB - TASA DE RECOGIDA DE BASURAS'),
        ('020', '020 - LQ - LICENC.APERTURA ACTIV.-ESTABLEC'),
        ('021', '021 - LQ - LICENCIAS AUTO-TAXIS'),
        ('022', '022 - LQ - LICENCIAS URBANISTICAS'),
        ('023', '023 - LQ - TASAS Y OTROS INGRESOS MUNICIPALES'),
        ('024', '024 - RB - ALCANTARILLADO'),
        ('025', '025 - RB - CANALIZAC.AGUAS'),
        ('026', '026 - RB - CANALONES'),
        ('027', '027 - RB - ESCAPARATES LETREROS VITRINAS'),
        ('028', '028 - RB - EXACCIONES S/INMUEBLES'),
        ('029', '029 - LQ - EXPLOTACION BAR POLIDEPORTIVO'),
        ('030', '030 - LQ - LIQUIDACION G.S.-COTOS CAZA'),
        ('031', '031 - RB - KIOSCOS VIA PUBLICA'),
        ('032', '032 - RB - MIRADORES'),
        ('033', '033 - RB - MOTORES Y TRANSFORMADORES'),
        ('034', '034 - LQ - OCUPACION VIA PUB. MATERIALES CONSTRUCCION'),
        ('035', '035 - LQ - OCUPACION V. PUB-MESAS/SILLAS '),
        ('036', '036 - LQ - OCUP.VIA PUB.-PUESTOS-BARRACAS '),
        ('037', '037 - RB - LICENCIAS/PARADAS AUTOTAXIS'),
        ('038', '038 - RB - PILAS DE BAÑOS'),
        ('039', '039 - RB - PRECIO PUBLICO ESCUELA DEPORTIVA'),
        ('040', '040 - RB - GUARDERIAS - ESC. INFANTILES'),
        ('041', '041 - RB - PRECIO PUBLICO LONJAS MERCADOS'),
        ('042', '042 - RB - REJAS'),
        ('043', '043 - LQ - CEMENTERIO MUNICIPAL'),
        ('044', '044 - LQ - SERVICIO DE MATADERO'),
        ('045', '045 - RB - SOLARES SIN EDIFICAR'),
        ('046', '046 - RB - TENENCIA DE PERROS'),
        ('047', '047 - RB - VADOS-ENTRADA VEHICULOS'),
        ('048', '048 - LQ - INFRACCIONES URBANISTICAS'),
        ('049', '049 - LQ - MULTAS TRAFICO DE VEHICULOS'),
        ('050', '050 - LQ - MULTAS Y SANCIONES'),
        ('051', '051 - RB - SUMINISTRO AGUA'),
        ('052', '052 - RB - LIQUIDACION DEUDA CONTRACTUAL'),
        ('053', '053 - RB - VIVIENDAS SOCIALES'),
        ('054', '054 - LQ - ACTAS GANADERIA'),
        ('055', '055 - LQ - ACTAS RUSTICA'),
        ('056', '056 - LQ - LICENC.OBRAS Y CONSTRUCCIONES'),
        ('074', '074 - LQ - IMPUESTO DE SUCESIONES Y DONACIONES'),
        ('075', '075 - LQ - ACTAS I. SUCESIONES/DONACIONES'),
        ('076', '076 - LQ - TRANSMISIONES ONEROSAS'),
        ('077', '077 - LQ - ACTOS JURIDICOS DOCUMENTADOS'),
        ('078', '078 - LQ - RESIDENCIA TIEMPO LIBRE'),
        ('079', '079 - LQ - MULTAS Y SANCIONES TRIBUTARIAS'),
        ('080', '080 - LQ - RECARGO LICENCIA FISCAL AÑOS ANTERIORES'),
        ('081', '081 - LQ - REINTEGROS DE PAGO DE EJERCICIOS CERRADOS'),
        ('082', '082 - LQ - CUOTA URBANIZACION'),
        ('083', '083 - LQ - LIQUIDACION DEL IMPUESTO VEHICULOS TRACCION\
        MECANICA'),
        ('084', '084 - RB - AGUA, BASURA Y ALCANTARILLADO'),
        ('085', '085 - RB - DESAGUES-CANALONES'),
        ('086', '086 - RB - CULTIVOS AGRICOLAS-ROTURADOS'),
        ('087', '087 - LQ - PRESTACION SERVICIO DERRIBOS'),
        ('088', '088 - LQ - UTILIZACION ALTAVOCES'),
        ('089', '089 - LQ - LIQUIDACION VADOS'),
        ('090', '090 - LQ - LIQUIDACION TASA BASURAS'),
        ('091', '091 - LQ - GESTION RECAUDACION MULTAS TRAFICO'),
        ('092', '092 - LQ - LIQUIDACION OCUPACION VIA PUBLICA'),
        ('093', '093 - LQ - LIQ. I.S/TRANSMISIONES PATRIMONIALES'),
        ('094', '094 - RB - NO ALCANTARILLADO'),
        ('095', '095 - RB - RECAUDACION EJECUTIVA TRIBUTOS LOCALES'),
        ('096', '096 - LQ - RECAUDACION EJECUTIVA SANCIONES AYUNTAMIENTO'),
        ('097', '097 - LQ - LIQUIDACION NICHOS'),
        ('098', '098 - LQ - AUTOLIQUIDACION IMP. VEHICULOS TRACCION MECANICA'),
        ('099', '099 - LQ - GASTOS DE CONSOLIDACION'),
        ('100', '100 - LQ - ESCAPARATES LETREROS VITRINAS'),
        ('101', '101 - LQ - DAÑOS FORESTALES '),
        ('102', '102 - LQ - TASA SERVICIO LONJAS MERCADOS '),
        ('119', '119 - LQ - APROVECHAMIENTOS AGRICOLAS Y FORESTALES '),
        ('125', '125 - RB - PUESTO PLAZA DE ABASTOS'),
        ('126', '126 - RB - TASA APARCAMIENTO MUNICIPAL'),
        ('127', '127 - LQ - TASA APARCAMIENTO MUNICIPAL '),
        ('128', '128 - RB - G.S.-COTOS CAZA'),
        ('143', '143 - LQ - SUBVENCIONES DE CAPITAL'),
        ('147', '147 - LQ - SUBVENCIONES DE CAPITAL'),
        ('163', '163 - RB - ESCUELAS INFANTILES'),
        ('167', '167 - LQ - LIQUID. SUMUNISTRO AGUA'),
        ('168', '168 - LQ - REINTEGRO IMPORTE'),
        ('169', '169 - LQ - TASA POR PUBLICIDAD CON VEHICULOS'),
        ('170', '170 - LQ - PRECIOS PUBLICOS MUNICIPALES'),
        ('171', '171 - LQ - CONTRIBUCIONES ESPECIALES'),
        ('177', '177 - RB - OCUPACION VIA PUBLICA'),
        ('178', '178 - RB - MERCADO SEMANAL'),
        ('179', '179 - LQ - LIQUIDACION MERCADO SEMANAL'),
        ('180', '180 - LQ - EXTRACCION DE CANTERA'),
        ('181', '181 - LQ - LIQUIDACION PUESTO PLAZA DE ABASTOS'),
        ('182', '182 - LQ - LIQUIDACION INGRESO DIRECTO'),
        ('183', '183 - LQ - LIQUIDACION DESAGUES-CANALONES'),
        ('184', '184 - RB - TASA CONSERVACION CEMENTERIO MUNICIPAL'),
        ('185', '185 - RB - MERCADO SEMANAL BENIEL'),
        ('186', '186 - LQ - LIQUIDACION MERCADO SEMANAL BENIEL'),
        ('187', '187 - LQ - TASACION COSTAS ASAMBLEA REGIONAL'),
        ('188', '188 - RB - IBI DE CARACTERÍSTICAS ESPECIALES '),
        ('189', '189 - LQ - PRESTACION DE SERVICIOS SANITARIOS'),
        ('190', '190 - LQ - TASAS SERVICIO MURCIANO DE SALUD'),
        ('191', '191 - LQ - PROCESAMIENTO HEMODERIVADOS'),
        ('192', '192 - LQ - CANONES Y OTROS INGRESOS DE DERECHO PUBLICO'),
        ('193', '193 - RB - TASA ANUAL RESERVA PUESTOS MERCADO'),
        ('194', '194 - RB - OCUPACION V. PUB-MESAS/SILLAS'),
        ('195', '195 - RB - TELEASISTENCIA DOMICILIARIA'),
        ('196', '196 - LQ - LIQUIDACION TELEASISTENCIA DOMICILIARIA'),
        ('197', '197 - LQ - REINTEGROS VOLUNTARIA P.A.C.'),
        ('198', '198 - LQ - LIQUIDACIONES REINTEGROS P.A.C.'),
        ('199', '199 - RB - CANON DE SANEAMIENTO'),
        ('200', '200 - RB - RECIBO I.B.I. URBANO'),
        ('201', '201 - RB - RECIBO I.B.I. RUSTICO'),
        ('202', '202 - RB - RECIBO IMPUESTO ACTIVIDADES ECONOMICAS'),
        ('203', '203 - RB - ROTULOS LETREROS'),
        ('204', '204 - LQ - LIQUIDACION ROTULOS LETREROS'),
        ('205', '205 - LQ - CANON DE VERTIDOS'),
        ('206', '206 - RB - APORTACION AYUNTAMIENTOS AL CONSORCIO RESIDUOS\
        SOLIDOS'),
        ('207', '207 - RB - INTERESES/COSTAS A FAVOR CONSORCIO RESIDUOS\
        SOLIDOS'),
        ('208', '208 - LQ - LIQUIDACION AGUA RESIDUAL USO RIEGO'),
        ('209', '209 - RB - SERVICIO ESTANCIAS DIURNAS'),
        ('210', '210 - RB - SERVICIO AYUDA DOMICILIO'),
        ('211', '211 - RB - APROVECHAMIENTOS ESPECIALES'),
        ('212', '212 - LQ - TASA OCUPACION SUELO/SUBSUELO/VUELO'),
        ('213', '213 - RB - TASA VOLADIZOS'),
        ('216', '216 - LQ - AUTOLIQUIDACION IMPUESTO INCR. VALOR TERRENOS\
        URBANOS'),
        ('217', '217 - LQ - INTERESES DE DEMORA AGENCIA'),
        ('220', '220 - LQ - TASAS Y OTROS INGRESOS DE DERECHO PUBLICO\
        DEL IMAS'),
        ('221', '221 - LQ - TASAS Y OTROS INGRESOS DE DERECHO PUBLICO\
        DEL SEF'),
        ('222', '222 - LQ - TASAS Y OTROS INGRESOS DE DERECHO PUBLICO\
        DE LA ARR'),
        ('223', '223 - LQ - MULTAS Y SANCIONES TRIBUTARIAS ARR'),
        ('224', '224 - RB - IMPUESTO BIENES INMUEBLES CARACTERISTICAS\
        ESPECIALES'),
        ('225', '225 - LQ - TASA DE VERTIDOS'),
        ('226', '226 - LQ - TASA LICENCIAS PRIMERA OCUPACION'),
        ('227', '227 - LQ - ESCUELAS MUNICIPALES'),
        ('228', '228 - LQ - LIQ. IMPUESTO BIENES DE CARACTERISTICAS\
        ESPECIALES'),
        ('229', '229 - RB - APORTACION DE AYUNTAMIENTOS A\
        CONSORCIOS/ORGANISMOS'),
        ('230', '230 - RB - REPARTOS ORDINARIOS DE COMUNIDADES DE REGANTES'),
        ('231', '231 - RB - DERRAMAS DE LAS COMUNIDADES DE REGANTES'),
        ('232', '232 - RB - INTERESES/COSTAS A FAVOR CONSORCIOS'),
        ('233', '233 - LQ - SANCIONES DE TRAFICO'),
        ('235', '235 - LQ - TASAS Y OTROS INGRESOS DE DERECHO PUBLICO\
        DE LA CARM'),
        ('236', '236 - LQ - RECARGO DECLARAC. EXTEMPORÁNEA SIN REQUERIMIENTO\
        PREVIO'),
        ('237', '237 - LQ - APROVECHAMIENTO ESPECIAL DEL DOMINIO PÚBLICO LOCAL\
        CON CAJEROS AUTOMÁTICOS'),
        ('238', '238 - RB - APROVECHAMIENTO ESPECIAL DEL DOMINIO PÚBLICO LOCAL\
        CON CAJEROS AUTOMÁTICOS'),
        ('239', '239 - LQ - LIQUIDACION TASA VOLADIZOS '),
        ('240', '240 - LQ - LIQUIDACIONES REINTEGROS P.A.C. FEAGA'),
        ('241', '241 - LQ - LIQUIDACIONES REINTEGROS P.A.C. FEADER'),
        ('242', '242 - LQ - INTERESES VOLUNTARIA LIQUIDACIONES REINTEGROS\
        P.A.C. FEAGA'),
        ('243', '243 - LQ - INTERESES VOLUNTARIA LIQUIDACIONES REINTEGROS\
        P.A.C. FEADER'),
        ('244', '244 - LQ - TASA DE ENTIDADES DE CONSERVACION'),
        ('245', '245 - LQ - APROVECHAMIENTO DOMINIO PÚBLICO LOCAL POR EMPRESAS\
        DE TELEFONÍA MÓVIL'),
        ('246', '246 - RB - APROVECHAMIENTO DOMINIO PÚBLICO LOCAL POR EMPRESAS\
        DE TELEFONÍA MÓVIL'),
        ('247', '247 - LQ - LIQUIDACIÓN IAE DERIVACIÓN DE RESPONSABILIDAD'),
        ('248', '248 - LQ - EJECUCION SUBSIDIARIA MUNICIPAL'),
        ('249', '249 - LQ - CUOTA ENTIDAD CONSERVADORA URBANISTICA'),
        ('251', '251 - RB - OTROS INGRESOS MUNICIPALES PERIODICOS'),
        ('252', '252 - LQ - TASA CONSORCIO EXTINCION INCENDIOS Y SALVAMENTO\
        CARM'),
        ('253', '253 - LQ - SANCIONES LEY 6/1997-FALTAS LEVES'),
        ('254', '254 - LQ - SANCIONES LEY 6/1997-FALTAS GRAVES'),
        ('255', '255 - LQ - SANCIONES LEY 6/1997-FALTAS MUY GRAVES'),
        ('258', '258 - LQ - EXIGENCIA DE REDUCCION DE SANCION TRIBUTARIA\
        ART.188.1 LEY 58/2003'),
        ('259', '259 - LQ - EXIGENCIA DE REDUCCION DE SANCION TRIBUTARIA\
        ART.188.3 LEY 58/2003'),
        ('260', '260 - LQ - LIQUIDACION INSPECCION DEL IMPUESTO SOBRE\
        ACTIVIDADES ECONOMICAS'),
        ('261', '261 - LQ - INTERESES DEMORA INSPECCION DEL IMPUESTO\
        SOBRE ACTIVIDADES ECONOMICAS'),
        ('262', '262 - LQ - SANCION DE INSPECCION'),
        ('263', '263 - LQ - SANCION DE TRAFICO')],
        string="Concept",
        help="Concept by which the settlement or receipt is made. It will\
            be applied to all transactions.",
        default="230")

    media_notice = fields.Selection([
        ('PE', 'Personal'),
        ('CT', 'Certificate'),
        ('BO', 'Bulletin'),
        ('SD', 'Electronic office'),
        ('MI', 'Manifestation interested party'),
        ('AG', 'Notifying agent'),
        ('DH', 'Enabled e-mail address'),
        ('ED', 'Edict')],
        string="Media notice",
        default="PE",
        help="Means used for the notification of the end of the voluntary\
            expiration date.\nIt will be applied to all payment lines.")

    notification_date = fields.Date(
        string='Notification date',
        help="Date on which the debtor was notified.\n\
            It will be applied to all payment lines.")

    # ATRM resume related fields
    atrm_filename = fields.Char(string="atrm filename")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id)
    atrm_total_amount = fields.Monetary(string="atrm total amount")

    # Methods
    @api.depends('payment_mode_id')
    def _compute_payment_mode_name(self):
        # @INFO: payment mode name ATRM (mandatory)
        self.payment_mode_name = self.payment_mode_id.name

    # On change payment mode force date_prefered
    @api.onchange('payment_mode_name')
    def _onchange_payment_mode_name(self):
        if self.payment_mode_name == 'ATRM':
            self.date_prefered = 'due'

    # Set agency
    @api.depends('payment_mode_name')
    def _compute_agency(self):
        self.agency = self._get_agency_config_atrm()

    def _get_next_shipment_num(self):
        # Get current year from today but update it
        # if shipment_date change
        current_year = datetime.today().year
        seq_num = self.env['ir.sequence'].search([(
            'code', '=', 'atrm_seq_shipment_number')])
        next_num = str(current_year) + seq_num.get_next_char(
            seq_num.number_next_actual)
        return next_num

    @api.onchange('shipment_date')
    def _onchange_shipment_date(self):
        date = datetime.strptime(self.shipment_date,
                                 DEFAULT_SERVER_DATE_FORMAT)
        current_year = str(date.year)
        seq_num = self.env['ir.sequence'].search([(
            'code', '=', 'atrm_seq_shipment_number')])
        next_num = str(current_year) + seq_num.get_next_char(
            seq_num.number_next_actual)
        self.shipment_num = next_num

    @api.model
    def create(self, vals):
        # Get current year from shipment_date value
        if vals.get('shipment_date'):
            current_year = vals.get('shipment_date')[:4]
        else:
            current_year = str(datetime.today().year)
        # Write vals and increase sequence
        vals['shipment_num'] = current_year +\
            self.env['ir.sequence'].next_by_code('atrm_seq_shipment_number')
        result = super(AccountPaymentOrder, self).create(vals)
        return result

    # Generate file
    @api.multi
    def generate_payment_file(self):
        self.ensure_one()
        _log = logging.getLogger(self.__class__.__name__)
        pay_method = self.payment_method_id

        if pay_method.code != 'debit_atrm':
            return super(AccountPaymentOrder, self).generate_payment_file()

        # Generate header
        # Position [01-01] Length 01 Format N
        header_registre_code = str(0)

        # Position [02-10] Length 09 Format AAAANNNNN
        shipment_num = self.shipment_num

        # Position [11-18] Length 08 Format DDMMAAAA
        shipment_date = datetime.strptime(
            self.shipment_date, '%Y-%m-%d').strftime("%d%m%Y")

        # Position [19-21] Length 03 Format NNN
        if self.agency == 'Unconfigured':
            raise ValidationError(_("The agency has not been configured.\
                Set it in Accounting/Settings."))
        else:
            agency_code = self.env['ir.values'].get_default(
                'account.config.settings', 'agency_code')

        # Position [22-27] Length 06 Format NNNNNN
        num_settlements = str(len(self.bank_line_ids)).zfill(6)

        # Position [28-40] Length 13 Format NNNNNNNNNNNNN
        # total_amount = (in the loop)

        # The positions from 41 to 65 are not used [filled by spaces]
        # @INFO: There are fields related with registry_type 2 and 3.
        blank_space1 = str(" " * 25)

        # Position [66-66] Length 01 Format (V,E or B)
        debt_period = self.debt_period

        # Positions [67- 838] Length 772
        if self.description:
            free_space = self.description[:772] or " "
            free_space_padded = free_space.ljust(772)
        else:
            free_space_padded = str(" " * 772)

        # Generate settlements
        # Position [01-01] Length 01 Format N
        sett_registre_code = str(self.registry_type)

        # Position [02-10] Length 09 Format YYYYNNNNN
        # shipment_num = (in the loop)

        # Position [11-16] Length 06 Format NNNNNN
        # entry_num = (in the loop)

        # Position [17-20] Length 04 Format YYYY
        # year = (in the loop)
        # @INFO: the year has to be the year of the debt

        # Position [21-23] Length 03 Format NNN
        if self.concept_code in self.CONCEPT_CODES_NOT_ALLOWED:
            raise ValidationError(_("The concept code %s is not allowed\
                at the moment." % self.concept_code))
        else:
            concept_code = str(self.concept_code)

        # Position [24-36] Length 13 Format NNNNNNNNNNN
        # fixed_num = (in the loop) [sequence atrm_seq_fix_num]

        # Position [37-45] Length 9
        # debtor_vat = (in the loop)

        # Position [46-170] Length 125
        # debtor_name = (in the loop)

        # Position [171-172] Length 2 Depend on debt_period (V, E or B)
        # debtor_public_road_acronym = (in the loop)

        # Position [173-272] Length 100 Depend on debt_period (V, E or B)
        # debtor_street = (in the loop)

        # Positions from 277 to 327 are not used [filled by spaces]
        blank_space3 = str(" " * 50)

        # Position [328-329] Length 2 Depend on debt_period (V, E or B)
        # debtor_province_ine_code = (in the loop)

        # Position [330-332] Length 3 Depend on debt_period (V, E or B)
        # debtor_county_ine_code = (in the loop)

        # Position [333-337] Length 5 Depend on debt_period (V, E or B)
        # debtor_county_zip = (in the loop)

        # Position [338-345] Length 08 Format DDMMYYYY Depend on concept_code
        # obligation_birthdate = (in the loop)

        # Position [346-353] Length 08 Format DDMMYYYY
        # settlement_date = (in the loop)

        # Position [354-354] Length 01 Format R or space
        recurred = " "

        # Position [355-367] Length 13 Format NNNNNNNNNNN
        # amount_to_voluntary_date = (in the loop)

        # Position [368-380] Length 13 Format NNNNNNNNNNN
        # amount_after_deadline = (in the loop)

        # Position [381-388] Length 8 Format DDMMYYYY
        # amount_after_deadline_date = (in the loop)

        # Position [389-396] Length 8 Format DDMMYYYY
        # voluntary_notification_date = (in the loop)

        # Position [397-398] Length 2
        # media_notice = (in the loop)

        # The positions from 407 to 629 are not used
        blank_space4 = str(" " * 223)

        # Position [630-729] Length 100
        # debt_description = (in the loop)

        # The positions from 730 to 838 are not used
        blank_space5 = str(" " * 109)

        # Loop
        # Reset variables
        total_amount = 0.0
        bank_lines = ""
        entry_num = 0

        # Iterate over bank lines
        for line in self.bank_line_ids:

            # Entry number (padded up to 6)
            entry_num += 1
            entry_num_padded = str(entry_num).zfill(6)

            # Check if bank line is already done
            if line.atrm_sent:
                raise ValidationError(_("The entry number %s has failed,\
                        the bank line %s seems that it has already been sent" %
                                        (entry_num_padded, line.name)))

            # Year of the debt
            # @ INFO: taken from invoice date

            # Fixed number (sequence)
            fixed_num = self.env['ir.sequence'].next_by_code(
                'atrm_seq_fix_number')

            # Associate this number to each bank line and set as done
            # @ INFO: in line write
            # line.atrm_ref = fixed_num
            # line.atrm_sent = True

            # Get vat (2 first characters are sliced)
            if line.partner_id.vat:
                debtor_vat = line.partner_id.vat[2:]
                if len(debtor_vat) > 9 or not \
                        line.partner_id.vat[3:-1].isdigit():
                    raise ValidationError(_("The entry number %s has failed,\
                            the vat %s for partner %s is not valid." %
                                            (entry_num_padded, debtor_vat,
                                             line.partner_id.name)))
            else:
                raise ValidationError(_("The entry number %s has failed,\
                    vat not found for partner %s." % (entry_num_padded,
                                                      line.partner_id.name)))

            # Get debtor name
            if line.partner_id.company_type == 'company':
                # @INFO: delete points and replace commas by spaces
                clean_debtor_name = \
                    line.partner_id.name.replace(".", "").replace(",", " ")
                debtor_name_padded = clean_debtor_name.ljust(125)
            elif line.partner_id.company_type == 'person':
                # @INFO: partner_second_lastname dependence
                if line.partner_id.lastname:
                    debtor_name = line.partner_id.lastname
                    if line.partner_id.lastname2:
                        debtor_name += ' ' + line.partner_id.lastname2
                else:
                    raise ValidationError(_("The entry number %s has failed,\
                        the lastname for partner %s not found." %
                                            (entry_num_padded,
                                             line.partner_id.name)))
                if line.partner_id.firstname:
                    debtor_name += ' ' + line.partner_id.firstname
                else:
                    raise ValidationError(_("The entry number %s has failed,\
                    the firstname for partner %s not found." %
                                            (entry_num_padded,
                                             line.partner_id.name)))
                debtor_name_padded = debtor_name.ljust(125)
            else:
                raise ValidationError(_("The entry number %s has failed,\
                    debtor name not found." % (entry_num_padded)))

            # Get others debtor params if debt_period is V
            if debt_period == "V":
                # @INFO: Try to get road acronym from street_type or give
                # default CL (the tax agency will process the errors).
                if line.partner_id.street_type:
                    debtor_public_road_acronym = line.partner_id.street_type
                else:
                    debtor_public_road_acronym = "CL"

                # @INFO: street_name is a dependence of partner_street_number
                if line.partner_id.street_name:
                    debtor_street = line.partner_id.street_name
                    debtor_street_padded = debtor_street.ljust(100)
                else:
                    raise ValidationError(_("The entry number %s has failed,\
                        debtor street not found for partner %s" %
                                            (entry_num_padded,
                                             line.partner_id.name)))

                # Get street number
                if line.partner_id.street_number:
                    debtor_street_number = \
                        str(line.partner_id.street_number).zfill(5)
                else:
                    debtor_street_number = str(" " * 5)

                # Simplify city name to compare
                if line.partner_id.city:
                    city_name_simplified = \
                        unicodedata.normalize(
                            'NFKD', line.partner_id.city).encode('ASCII',
                                                                 'ignore'
                                                                 ).upper()

                    # Get ine codes using partner city simplified
                    ine_codes = \
                        self.env['res.ine.codes'].search([(
                            'city_name_simplified', '=',
                            city_name_simplified)])

                    if ine_codes:
                        debtor_province_ine_code = \
                            str(ine_codes.ine_code_province).zfill(2)
                        debtor_county_ine_code = \
                            str(ine_codes.ine_code_city).zfill(3)
                    else:
                        raise ValidationError(_("The entry number %s has\
                            failed, debtor ine city code not found for city\
                            %s.\nSometimes this is because the name of the\
                            city is not well written (first capital letter,\
                            accents, hyphens, etc.)." %
                                                (entry_num_padded,
                                                 line.partner_id.city)))
                else:
                    raise ValidationError(_("The entry number %s has failed,\
                        debtor city not found for partner %s" %
                                            (entry_num_padded,
                                             line.partner_id.name)))

                # Zip
                if line.partner_id.zip:
                    debtor_county_zip = line.partner_id.zip
                else:
                    raise ValidationError(_("The entry number %s has failed,\
                        debtor zip not found for partner %s" %
                                            (entry_num_padded,
                                             line.partner_id.name)))

            # If debt_period is E or B these fields are not necessary
            else:
                debtor_public_road_acronym = str(" " * 2)
                debtor_street_padded = str(" " * 100)
                debtor_street_number = str(" " * 5)
                debtor_province_ine_code = str(" " * 2)
                debtor_county_ine_code = str(" " * 3)
                debtor_county_zip = str(" " * 5)

            # Get dates and year
            for l in line.payment_line_ids:
                if line.name == l.bank_line_id.name:
                    # Get obligation_birthdate (invoice date)
                    obligation_birthdate = \
                        datetime.strptime(l.move_line_id.date,
                                          '%Y-%m-%d').strftime("%d%m%Y")
                    # Get year
                    year = obligation_birthdate[4:]
                    # Get settlement date (maturity date)
                    settlement_date = datetime.strptime(
                        l.move_line_id.date_maturity,
                        '%Y-%m-%d').strftime("%d%m%Y")

            # Get amount voluntary (equal in V, E or B)
            # @INFO: Has to be between max. and min. allowed
            #        by the agency agreement
            agency_max = self.env['ir.values'].get_default(
                'account.config.settings', 'agency_max_amount')
            agency_min = self.env['ir.values'].get_default(
                'account.config.settings', 'agency_min_amount')

            if line.amount_currency > agency_max or \
               line.amount_currency < agency_min:
                raise ValidationError(_("The entry number %s has failed,\
                    the amount %s exceeds the limits allowed by the agency\
                    agreement." % (entry_num_padded, line.amount_currency)))
            else:
                amount_to_voluntary_date = line.amount_currency
                amount_to_voluntary_date_padded = \
                    str(amount_to_voluntary_date).zfill(13).replace('.', ',')

            # Sum amount to total_amount (for header)
            total_amount += line.amount_currency

            # Position [355-398] depends on debt_period
            if self.debt_period == "V":
                amount_after_deadline = str(" " * 13)
                amount_after_deadline_date = str(" " * 8)
                voluntary_notification_date = str(" " * 8)
                media_notice = str(" " * 2)
                voluntary_expiration_date = str(" " * 8)
            else:
                amount_after_deadline = str(" " * 13)      # Never filled
                amount_after_deadline_date = str(" " * 8)  # Never filled
                voluntary_notification_date = datetime.strptime(
                    self.notification_date, '%Y-%m-%d').strftime("%d%m%Y")
                media_notice = self.media_notice
                # Set voluntary_expiration_date
                # If notified between 1 and 15, until 20 same month
                # If notified between 16 and 31, until 5 next month
                notification_day = int(datetime.strptime(
                    self.notification_date, '%Y-%m-%d').strftime("%d"))
                if 1 <= notification_day <= 15:
                    voluntary_expiration_date = \
                        datetime.strptime(
                            self.notification_date,
                            '%Y-%m-%d').replace(day=20).strftime("%d%m%Y")
                else:
                    # Increase notification date by one month
                    next_month_date = \
                        datetime.strptime(
                            self.notification_date,
                            "%Y-%m-%d") + relativedelta(months=+1)
                    voluntary_expiration_date = \
                        next_month_date.replace(day=5).strftime("%d%m%Y")

            # Check dates ranges and year
            # 01.- Check that obligation_birthdate is previous or equal
            #      to settlement_date
            obli_birthdate = datetime.strptime(obligation_birthdate,
                                               '%d%m%Y').strftime('%Y-%m-%d')
            sett_date = datetime.strptime(settlement_date,
                                          '%d%m%Y').strftime('%Y-%m-%d')
            if obli_birthdate > sett_date:
                raise ValidationError(_("The entry number %s has failed,\
                    the obligation birthdate (%s) is after the settlement\
                    date (%s)." % (entry_num_padded, obligation_birthdate,
                                   settlement_date)))

            # 02.- Check that settlement_date is previous to the current date
            #      and previous or equal to voluntary expiration date if E or B
            current_date = datetime.today().strftime('%Y-%m-%d')
            if sett_date >= current_date:
                raise ValidationError(_("The entry number %s has failed,\
                    the settlement date (%s) is after the current date (%s)."
                                        % (entry_num_padded,
                                           sett_date, current_date)))

            if self.debt_period != "V":
                vol_exp_date = datetime.strptime(voluntary_expiration_date,
                                                 "%d%m%Y").strftime('%Y-%m-%d')
                if sett_date > vol_exp_date:
                    raise ValidationError(_("The entry number %s has failed,\
                        the settlement date (%s) is after expiration date \
                        (%s)." % (entry_num_padded, sett_date, vol_exp_date)))

            # 03.- Check that year is previous or equal to current year and
            #      not previous to 1986
            current_year = datetime.today().strftime('%Y')
            if year > current_year:
                raise ValidationError(_("The entry number %s has failed,\
                        the year (%s) is after of current year (%s)."
                                        % (entry_num_padded, year,
                                           current_year)))
            if year < "1986":
                raise ValidationError(_("The entry number %s has failed,\
                        the year (%s) is after 1986."
                                        % (entry_num_padded, year)))

            # The positions from 407 to 629 are not used
            # blank_space4 = str(" " * 223)

            # Get debt_description
            # @INFO: We take the invoice name to fill this field
            #        which becomes communication in bank_line
            debt_description = line.communication or ""
            debt_description_padded = str(debt_description).ljust(100)

            # The positions from 730 to 838 are not used
            # blank_space5 = str(" " * 109)

            # Log bank line fields with length [and expected length]
            _log.info('NEW BANK LINE. Number %s #############################'
                      % str(entry_num).zfill(2))
            _log.info('BANK LINE FIELD Registre code     (length %s [001]): %s'
                      % (str(len(sett_registre_code)).zfill(3),
                         sett_registre_code))
            _log.info('BANK LINE FIELD Shipment number   (length %s [009]): %s'
                      % (str(len(shipment_num)).zfill(3), shipment_num))
            _log.info('BANK LINE FIELD Entry number      (length %s [006]): %s'
                      % (str(len(entry_num_padded)).zfill(3),
                         entry_num_padded))
            _log.info('BANK LINE FIELD Year              (length %s [004]): %s'
                      % (str(len(year)).zfill(3), year))
            _log.info('BANK LINE FIELD Concept code      (length %s [003]): %s'
                      % (str(len(concept_code)).zfill(3), concept_code))
            _log.info('BANK LINE FIELD Fixed num         (length %s [013]): %s'
                      % (str(len(fixed_num)).zfill(3), fixed_num))
            _log.info('BANK LINE FIELD Debtor VAT        (length %s [009]): %s'
                      % (str(len(debtor_vat)).zfill(3), debtor_vat))
            _log.info('BANK LINE FIELD Debtor name       (length %s [125]): %s'
                      % (str(len(debtor_name_padded)).zfill(3),
                         debtor_name_padded))
            _log.info('BANK LINE FIELD Debtor st. type   (length %s [002]): %s'
                      % (str(len(debtor_public_road_acronym)).zfill(3),
                         debtor_public_road_acronym))
            _log.info('BANK LINE FIELD Debtor st. name   (length %s [100]): %s'
                      % (str(len(debtor_street_padded)).zfill(3),
                         debtor_street_padded))
            _log.info('BANK LINE FIELD Debtor st. num    (length %s [005]): %s'
                      % (str(len(debtor_street_number)).zfill(3),
                         debtor_street_number))
            _log.info('BANK LINE FIELD Blank spaces 3    (length %s [050]): %s'
                      % (str(len(blank_space3)).zfill(3), blank_space3))
            _log.info('BANK LINE FIELD INE Province      (length %s [002]): %s'
                      % (str(len(debtor_province_ine_code)).zfill(3),
                         debtor_province_ine_code))
            _log.info('BANK LINE FIELD INE County        (length %s [003]): %s'
                      % (str(len(debtor_county_ine_code)).zfill(3),
                         debtor_county_ine_code))
            _log.info('BANK LINE FIELD Debtor ZIP        (length %s [005]): %s'
                      % (str(len(debtor_county_zip)).zfill(3),
                         debtor_county_zip))
            _log.info('BANK LINE FIELD Obligation birth  (length %s [008]): %s'
                      % (str(len(obligation_birthdate)).zfill(3),
                         obligation_birthdate))
            _log.info('BANK LINE FIELD Settlement date   (length %s [008]): %s'
                      % (str(len(settlement_date)).zfill(3),
                         settlement_date))
            _log.info('BANK LINE FIELD Recurred          (length %s [001]): %s'
                      % (str(len(recurred)).zfill(3), recurred))
            _log.info('BANK LINE FIELD Amount (vol date) (length %s [013]): %s'
                      % (str(len(amount_to_voluntary_date_padded)).zfill(3),
                         amount_to_voluntary_date_padded))
            _log.info('BANK LINE FIELD Amount (deadline) (length %s [013]): %s'
                      % (str(len(amount_after_deadline)).zfill(3),
                         amount_after_deadline))
            _log.info('BANK LINE FIELD Vol notifi date   (length %s [008]): %s'
                      % (str(len(voluntary_notification_date)).zfill(3),
                         voluntary_notification_date))
            _log.info('BANK LINE FIELD Media notice      (length %s [002]): %s'
                      % (str(len(media_notice)).zfill(3), media_notice))
            _log.info('BANK LINE FIELD Vol expira date   (length %s [008]): %s'
                      % (str(len(voluntary_expiration_date)).zfill(3),
                         voluntary_expiration_date))
            _log.info('BANK LINE FIELD Blank spaces 4    (length %s [223]): %s'
                      % (str(len(blank_space4)).zfill(3), blank_space4))
            _log.info('BANK LINE FIELD Debt description  (length %s [100]): %s'
                      % (str(len(debt_description_padded)).zfill(3),
                         debt_description_padded))
            _log.info('BANK LINE FIELD Blank spaces 5    (length %s [109]): %s'
                      % (str(len(blank_space5)).zfill(3), blank_space5))

            # Construct bank line
            bank_line = sett_registre_code + shipment_num + entry_num_padded\
                + year + concept_code + fixed_num + debtor_vat +\
                debtor_name_padded + debtor_public_road_acronym +\
                debtor_street_padded + debtor_street_number + blank_space3\
                + debtor_province_ine_code + debtor_county_ine_code +\
                debtor_county_zip + obligation_birthdate + settlement_date +\
                recurred + amount_to_voluntary_date_padded +\
                amount_after_deadline + amount_after_deadline_date +\
                voluntary_notification_date + media_notice +\
                voluntary_expiration_date + blank_space4 +\
                debt_description_padded + blank_space5 + "\r\n"

            _log.info('FULL BANK LINE                    (length %s [840]): %s'
                      % (str(len(bank_line)).zfill(3), bank_line))

            # Add to bank_lines
            bank_lines += bank_line

        # Construct header (wait until to have the total amount)
        # Change decimal point by comma total_amount
        total_amount_padded = str(total_amount).zfill(13).replace('.', ',')

        # Set atrm_total_amount for ATRM resume
        self.atrm_total_amount = total_amount

        # Log header fields with length
        _log.info('HEADER FIELD Header registry code (length %s [001]): %s'
                  % (str(len(header_registre_code)).zfill(3),
                     header_registre_code))
        _log.info('HEADER FIELD Shipment number      (length %s [009]): %s'
                  % (str(len(shipment_num)).zfill(3), shipment_num))
        _log.info('HEADER FIELD Shipment date        (length %s [008]): %s'
                  % (str(len(shipment_date)).zfill(3), shipment_date))
        _log.info('HEADER FIELD Agency code          (length %s [003]): %s'
                  % (str(len(agency_code)).zfill(3), agency_code))
        _log.info('HEADER FIELD Num of settlements   (length %s [009]): %s'
                  % (str(len(num_settlements)).zfill(3), num_settlements))
        _log.info('HEADER FIELD Total amount         (length %s [006]): %s'
                  % (str(len(total_amount_padded)).zfill(3),
                     total_amount_padded))
        _log.info('HEADER FIELD Blank spaces 1       (length %s [025]): %s'
                  % (str(len(blank_space1)).zfill(3), blank_space1))
        _log.info('HEADER FIELD Debt period          (length %s [001]): %s'
                  % (str(len(debt_period)).zfill(3), debt_period))
        _log.info('HEADER FIELD Description          (length %s [772]): %s'
                  % (str(len(free_space_padded)).zfill(3),
                     free_space_padded))

        header = header_registre_code + shipment_num + shipment_date + \
            agency_code + num_settlements + total_amount_padded + \
            blank_space1 + debt_period + free_space_padded + "\r\n"

        _log.info('FULL HEADER LINE                  (length %s [840]): %s'
                  % (str(len(header)).zfill(3), header))

        # Send to the file
        payment_file_str = \
            header.encode('ascii', 'ignore') + \
            bank_lines.encode('ascii', 'ignore')

        # Generate filename (YYYYMMMNNNNN.txt)
        #  YYYY  -- Year of dispatch of the charge. Current year.
        #  MMM   -- Code of the agency or municipality that sends the file
        #  NNNNN -- This must be a number that identifies the charge among
        #           those issued by the municipality for the year of shipment
        filename = shipment_num[:4] + agency_code + shipment_num[4:] + ".txt"

        # Set atrm_filename for ATRM resume
        self.atrm_filename = filename

        line.write({
                'atrm_ref': fixed_num,
                'atrm_sent': True,
        })

        return payment_file_str, filename
