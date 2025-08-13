# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from lxml import etree
from cryptography import x509
from cryptography.x509.name import _NAMEOID_TO_NAME
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.backends import default_backend

import pytz
import random
import base64
import hashlib
import logging

try:
    import xmlsig
except(ImportError, IOError) as err:
    logging.info(err)

from odoo import models, fields, tools, _, api
from odoo.exceptions import Warning as UserError, ValidationError

logger = logging.Logger("facturae")


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    correction_method = fields.Selection(
        selection=[
            ('01', 'Rectificación íntegra'),
            ('02', 'Rectificación por diferencias'),
            ('03', 'Rectificación por descuento por volumen de operaciones '
                   'durante un periodo'),
            ('04', 'Autorizadas por la Agencia Tributaria')
        ]
    )

    facturae_refund_reason = fields.Selection(
        selection=[
            ('01', 'Número de la factura'),
            ('02', 'Serie de la factura'),
            ('03', 'Fecha expedición'),
            ('04', 'Nombre y apellidos/Razón social - Emisor'),
            ('05', 'Nombre y apellidos/Razón social - Receptor'),
            ('06', 'Identificación fiscal Emisor/Obligado'),
            ('07', 'Identificación fiscal Receptor'),
            ('08', 'Domicilio Emisor/Obligado'),
            ('09', 'Domicilio Receptor'),
            ('10', 'Detalle Operación'),
            ('11', 'Porcentaje impositivo a aplicar'),
            ('12', 'Cuota tributaria a aplicar'),
            ('13', 'Fecha/Periodo a aplicar'),
            ('14', 'Clase de factura'),
            ('15', 'Literales legales'),
            ('16', 'Base imponible'),
            ('80', 'Cálculo de cuotas repercutidas'),
            ('81', 'Cálculo de cuotas retenidas'),
            ('82', 'Base imponible modificada por devolución de envases'
                   '/embalajes'),
            ('83', 'Base imponible modificada por descuentos y '
                   'bonificaciones'),
            ('84', 'Base imponible modificada por resolución firme, judicial '
                   'o administrativa'),
            ('85', 'Base imponible modificada cuotas repercutidas no '
                   'satisfechas. Auto de declaración de concurso')
        ]
    )

    integration_ids = fields.One2many(
        comodel_name='account.invoice.integration',
        inverse_name='invoice_id',
        copy=False
    )

    start_date = fields.Date(
        string="Start Date",
        help="Start date of the period to be included in the invoice",
        required=False
    )

    end_date = fields.Date(
        string="End Date",
        help="End date of the period to be included in the invoice",
        required=False
    )

    round_decimal = fields.Boolean(
        string="Round Decimal",
        help="Round decimals to two digits on all amounts in the invoice",
        required=False
    )

    service_date = fields.Date(
        string="Service/Supply Date",
        help="Date of the service or supply",
        required=False
    )

    @api.depends('integration_ids')
    def _compute_integrations_count(self):
        self.integration_count = len(self.integration_ids)

    integration_count = fields.Integer(
        compute="_compute_integrations_count",
        string='# of Integrations', copy=False, default=0)

    @api.depends('integration_ids', 'partner_id')
    def _compute_can_integrate(self):
        for method in self.partner_id.invoice_integration_method_ids:
            if not self.env['account.invoice.integration'].search(
                    [('invoice_id', '=', self.id),
                     ('method_id', '=', method.id)]):
                self.can_integrate = True
                return
        self.can_integrate = False

    can_integrate = fields.Boolean(compute="_compute_can_integrate")

    # New fields from v14 [Added on 22.03.2024]
    facturae_receiver_transaction_reference = fields.Char(
        string="Transaction Reference")
    facturae_receiver_contract_reference = fields.Char(
        string="Contract Reference")

    @api.multi
    def action_integrations(self):
        self.ensure_one()
        for method in self.partner_id.invoice_integration_method_ids:
            if not self.env['account.invoice.integration'].search(
                    [('invoice_id', '=', self.id),
                     ('method_id', '=', method.id)]):
                method.create_integration(self)
        return self.action_view_integrations()

    @api.multi
    def action_view_integrations(self):
        self.ensure_one()
        action = self.env.ref(
            'l10n_es_facturae.invoice_integration_action')
        result = action.read()[0]
        result['context'] = {'default_invoice_id': self.id}
        integrations = self.env['account.invoice.integration'].search([
            ('invoice_id', '=', self.id)
        ])

        if len(integrations) != 1:
            result['domain'] = "[('id', 'in', " + \
                               str(integrations.ids) + \
                               ")]"
        elif len(integrations) == 1:
            res = self.env.ref('account.invoice.integration.form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = integrations.id
        return result

    def get_exchange_rate(self, euro_rate, currency_rate):
        if not euro_rate and not currency_rate:
            return fields.Datetime.now().strftime('%Y-%m-%d')
        if not currency_rate:
            return fields.Datetime.from_string(euro_rate.name
                                               ).strftime('%Y-%m-%d')
        if not euro_rate:
            return fields.Datetime.from_string(currency_rate.name
                                               ).strftime('%Y-%m-%d')
        currency_date = fields.Datetime.from_string(currency_rate.name)
        euro_date = fields.Datetime.from_string(currency_rate.name)
        if currency_date < euro_date:
            return currency_date.strftime('%Y-%m-%d')
        return euro_date.strftime('%Y-%m-%d')

    def get_refund_reason_string(self):
        return dict(
            self.fields_get(
                allfields=['facturae_refund_reason']
            )['facturae_refund_reason']['selection']
        )[self.facturae_refund_reason]

    def get_correction_method_string(self):
        return dict(
            self.fields_get(allfields=['correction_method'])[
                'correction_method']['selection'])[self.correction_method]

    def _get_valid_invoice_statuses(self):
        return ['open', 'paid']

    def validate_facturae_fields(self):
        for line in self.invoice_line_ids:
            if not line.invoice_line_tax_ids:
                raise ValidationError(_('Taxes not provided in invoice line '
                                        '%s') % line.name)
        if not self.partner_id.vat:
            raise ValidationError(_('Partner vat not provided'))
        if not self.company_id.partner_id.vat:
            raise ValidationError(_('Company vat not provided'))
        if len(self.partner_id.vat) < 3:
            raise ValidationError(_('Partner vat is too small'))
        if not self.partner_id.state_id:
            raise ValidationError(_('Partner state not provided'))
        if len(self.company_id.vat) < 3:
            raise ValidationError(_('Company vat is too small'))
        if not self.payment_mode_id:
            raise ValidationError(_('Payment mode is required'))
        if self.payment_mode_id.facturae_code == '02':
            if not self.mandate_id:
                raise ValidationError(_('Mandate is missing'))
            if not self.mandate_id.partner_bank_id:
                raise ValidationError(_('Partner bank in mandate is missing'))
            if len(self.mandate_id.partner_bank_id.bank_id.bic) != 11:
                raise ValidationError(_('Mandate account BIC must be 11'))
            if len(self.mandate_id.partner_bank_id.acc_number) < 5:
                raise ValidationError(_('Mandate account is too small'))
        else:
            if self.partner_bank_id:
                partner_bank_id = self.partner_bank_id
            # Get first bank_id from partner and set
            # elif (not self.partner_bank_id and
            #         self.partner_id.bank_account_count > 0):
            #     self.partner_bank_id = partner_bank_id = \
            #         self.partner_id.bank_ids[0]
            # Get first bank_id from payment mode journal and set
            elif self.payment_mode_id.show_bank_account_from_journal:
                if self.payment_mode_id.bank_account_link == "fixed":
                    self.partner_bank_id = partner_bank_id = \
                        self.payment_mode_id.fixed_journal_id.bank_account_id
                else:
                    self.partner_bank_id = partner_bank_id = \
                        self.payment_mode_id.variable_journal_ids.mapped(
                            "bank_account_id")[0]
            else:
                raise ValidationError(_('Partner bank is missing'))
            if partner_bank_id.bank_id.bic and len(
                    partner_bank_id.bank_id.bic) != 11:
                raise ValidationError(_('Selected account BIC must be 11'))
            if len(partner_bank_id.acc_number) < 5:
                raise ValidationError(_('Selected account is too small'))
        if self.state not in self._get_valid_invoice_statuses():
            raise ValidationError(_('You can only create Factura-E files for '
                                    'invoices that have been validated.'))
        return

    def get_facturae(self, firmar_facturae):

        def _sign_file(public_crt, private_key, request):
            rand_min = 1
            rand_max = 99999
            signature_id = "Signature%05d" % random.randint(rand_min, rand_max)
            signed_properties_id = signature_id + "-SignedProperties%05d" % \
                random.randint(rand_min, rand_max)
            key_info_id = "KeyInfo%05d" % random.randint(rand_min, rand_max)
            reference_id = "Reference%05d" % random.randint(rand_min, rand_max)
            object_id = "Object%05d" % random.randint(rand_min, rand_max)
            etsi = "http://uri.etsi.org/01903/v1.3.2#"
            sig_policy_identifier = (
                "http://www.facturae.es/"
                "politica_de_firma_formato_facturae/"
                "politica_de_firma_formato_facturae_v3_1"
                ".pdf")
            sig_policy_hash_value = "Ohixl6upD6av8N7pEvDABhEL6hM="
            root = etree.fromstring(request)
            sign = xmlsig.template.create(
                c14n_method=xmlsig.constants.TransformInclC14N,
                sign_method=xmlsig.constants.TransformRsaSha1,
                name=signature_id,
                ns="ds")
            key_info = xmlsig.template.ensure_key_info(sign, name=key_info_id)
            x509_data = xmlsig.template.add_x509_data(key_info)
            xmlsig.template.x509_data_add_certificate(x509_data)
            xmlsig.template.add_key_value(key_info)
            with open(public_crt, "rb") as f:
                certificate = x509.load_pem_x509_certificate(
                    f.read(), backend=default_backend())
            xmlsig.template.add_reference(
                sign,
                xmlsig.constants.TransformSha1,
                uri="#" + signed_properties_id,
                uri_type="http://uri.etsi.org/01903#SignedProperties",
            )
            xmlsig.template.add_reference(
                sign, xmlsig.constants.TransformSha1, uri="#" + key_info_id)
            ref = xmlsig.template.add_reference(
                sign, xmlsig.constants.TransformSha1, name=reference_id, uri=""
            )
            xmlsig.template.add_transform(
                ref, xmlsig.constants.TransformEnveloped)
            object_node = etree.SubElement(
                sign,
                etree.QName(xmlsig.constants.DSigNs, "Object"),
                nsmap={"etsi": etsi},
                attrib={xmlsig.constants.ID_ATTR: object_id},
            )
            qualifying_properties = etree.SubElement(
                object_node,
                etree.QName(etsi, "QualifyingProperties"),
                attrib={"Target": "#" + signature_id},
            )
            signed_properties = etree.SubElement(
                qualifying_properties,
                etree.QName(etsi, "SignedProperties"),
                attrib={xmlsig.constants.ID_ATTR: signed_properties_id},
            )
            signed_signature_properties = etree.SubElement(
                signed_properties, etree.QName(
                    etsi, "SignedSignatureProperties"))
            now = datetime.now().replace(microsecond=0, tzinfo=pytz.utc)
            etree.SubElement(
                signed_signature_properties, etree.QName(etsi, "SigningTime")
            ).text = now.isoformat()
            signing_certificate = etree.SubElement(
                signed_signature_properties, etree.QName(
                    etsi, "SigningCertificate"))
            signing_certificate_cert = etree.SubElement(
                signing_certificate, etree.QName(etsi, "Cert")
            )
            cert_digest = etree.SubElement(
                signing_certificate_cert, etree.QName(etsi, "CertDigest")
            )
            etree.SubElement(
                cert_digest,
                etree.QName(xmlsig.constants.DSigNs, "DigestMethod"),
                attrib={"Algorithm": "http://www.w3.org/2000/09/xmldsig#sha1"},
            )
            hash_cert = hashlib.sha1(certificate.public_bytes(Encoding.DER))
            etree.SubElement(
                cert_digest, etree.QName(
                    xmlsig.constants.DSigNs, "DigestValue")
            ).text = base64.b64encode(hash_cert.digest())
            issuer_serial = etree.SubElement(
                signing_certificate_cert, etree.QName(etsi, "IssuerSerial")
            )
            XMLSIG_NAMEOID_TO_NAME = _NAMEOID_TO_NAME.copy()
            cert_issuer_data = []
            cert_issuer_data_raw = certificate.issuer.rdns
            for data in cert_issuer_data_raw:
                dn_data = []
                for attribute in data._attributes:
                    key = XMLSIG_NAMEOID_TO_NAME.get(
                        attribute.oid, "OID.%s" % attribute.oid.dotted_string)
                    dn_data.insert(0, u"{}={}".format(key, attribute.value))
                cert_issuer_data.insert(0, "+".join(dn_data))
            cert_issuer = ",".join(cert_issuer_data)
            etree.SubElement(
                issuer_serial,
                etree.QName(xmlsig.constants.DSigNs, 'X509IssuerName')
            ).text = cert_issuer
            etree.SubElement(
                issuer_serial,
                etree.QName(xmlsig.constants.DSigNs, 'X509SerialNumber')
            ).text = str(certificate.serial_number)
            signature_policy_identifier = etree.SubElement(
                signed_signature_properties,
                etree.QName(etsi, "SignaturePolicyIdentifier"),
            )
            signature_policy_id = etree.SubElement(
                signature_policy_identifier, etree.QName(
                    etsi, "SignaturePolicyId"))
            sig_policy_id = etree.SubElement(
                signature_policy_id, etree.QName(etsi, "SigPolicyId")
            )
            etree.SubElement(
                sig_policy_id, etree.QName(etsi, "Identifier")
            ).text = sig_policy_identifier
            etree.SubElement(
                sig_policy_id, etree.QName(etsi, "Description")
            ).text = u"Política de Firma FacturaE v3.1"
            sig_policy_hash = etree.SubElement(
                signature_policy_id, etree.QName(etsi, "SigPolicyHash")
            )
            etree.SubElement(
                sig_policy_hash,
                etree.QName(xmlsig.constants.DSigNs, "DigestMethod"),
                attrib={"Algorithm": "http://www.w3.org/2000/09/xmldsig#sha1"},
            )
            hash_value = sig_policy_hash_value
            etree.SubElement(
                sig_policy_hash, etree.QName(
                    xmlsig.constants.DSigNs, "DigestValue")).text = hash_value
            signer_role = etree.SubElement(
                signed_signature_properties, etree.QName(etsi, "SignerRole")
            )
            claimed_roles = etree.SubElement(
                signer_role, etree.QName(etsi, "ClaimedRoles"))
            etree.SubElement(
                claimed_roles, etree.QName(etsi, "ClaimedRole")
            ).text = "supplier"  # supplier/emisor
            signed_data_object_properties = etree.SubElement(
                signed_properties, etree.QName(
                    etsi, "SignedDataObjectProperties"))
            data_object_format = etree.SubElement(
                signed_data_object_properties,
                etree.QName(etsi, "DataObjectFormat"),
                attrib={"ObjectReference": "#" + reference_id},
            )
            etree.SubElement(
                data_object_format, etree.QName(etsi, "Description")
            ).text = "Factura"
            etree.SubElement(
                data_object_format, etree.QName(etsi, "MimeType")
            ).text = "text/xml"

            ctx = xmlsig.SignatureContext()
            ctx.x509 = certificate
            ctx.public_key = certificate.public_key()
            with open(private_key, "rb") as f:
                ctx.private_key = serialization.load_pem_private_key(
                    f.read(), password=None, backend=default_backend())
            root.append(sign)
            ctx.sign(sign)
            return etree.tostring(root, xml_declaration=True, encoding="UTF-8")

        self.validate_facturae_fields()

        report = self.env.ref('l10n_es_facturae.report_facturae')
        xml_facturae = \
            report.render_report(self.ids, report.report_name, {})[0]
        # Delete white spaces
        tree = etree.fromstring(
            xml_facturae, etree.XMLParser(
                remove_blank_text=True, encoding='UTF-8'))
        xml_facturae = etree.tostring(
            tree, xml_declaration=True, encoding='UTF-8')
        self._validate_facturae(xml_facturae)

        if (self.company_id.facturae_cert_public_key and
                self.company_id.facturae_cert_private_key and firmar_facturae):
            public_crt, private_key = (
                self.env["res.company"].sudo().facturae_cert_get_certificates(
                    self.company_id))
            file_name = (_(
                'facturae') + '_' + self.number + '.xsig').replace('/', '-')
            invoice_file = _sign_file(public_crt, private_key, xml_facturae)
        else:
            invoice_file = xml_facturae
            file_name = (_(
                'facturae') + '_' + self.number + '.xml').replace('/', '-')

        return invoice_file, file_name

    def _get_facturae_schema_file(self):
        return tools.file_open("Facturaev3_2_2.xsd",
                               subdir="addons/l10n_es_facturae/data")

    def _validate_facturae(self, xml_string):
        facturae_schema = etree.XMLSchema(
            etree.parse(self._get_facturae_schema_file()))
        try:
            facturae_schema.assertValid(etree.fromstring(xml_string))
        except Exception as e:
            logger.warning(
                "The XML file is invalid against the XML Schema Definition")
            logger.warning(xml_string)
            logger.warning(e)
            raise UserError(
                _("The generated XML file is not valid against the official "
                  "XML Schema Definition. The generated XML file and the "
                  "full error have been written in the server logs. Here "
                  "is the error, which may give you an idea on the cause "
                  "of the problem : %s") % str(e))
        return True
