# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# Copyright 2017 Diagram Software S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64
import contextlib
import logging
import os
import tempfile

from odoo import _, exceptions, fields, models, release
from odoo.exceptions import ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)

try:
    import cryptography
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        NoEncryption,
        PrivateFormat,
        pkcs12,
    )
except (ImportError, IOError) as err:
    _logger.debug(err)

if tuple(map(int, cryptography.__version__.split("."))) < (3, 0):
    _logger.warning(
        "Cryptography version is not supported. Upgrade to 3.0.0 or greater."
    )


@contextlib.contextmanager
def pfx_to_pem(p12, directory=None):
    with tempfile.NamedTemporaryFile(
        prefix="private_", suffix=".pem", delete=False, dir=directory
    ) as t_pem:
        with open(t_pem.name, "wb") as f_pem:
            f_pem.write(
                p12[0].private_bytes(
                    Encoding.PEM,
                    format=PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=NoEncryption(),
                )
            )
            f_pem.close()
        yield t_pem.name


@contextlib.contextmanager
def pfx_to_crt(p12, directory=None):
    with tempfile.NamedTemporaryFile(
        prefix="public_", suffix=".crt", delete=False, dir=directory
    ) as t_crt:
        with open(t_crt.name, "wb") as f_crt:
            f_crt.write(p12[1].public_bytes(Encoding.PEM))
            f_crt.close()
        yield t_crt.name


class L10nEsFacturaeCertificatePassword(models.TransientModel):
    _name = "l10n.es.facturae.certificate.password"
    _description = "Wizard to Load Certificate"

    password = fields.Char(string="Password", required=True)

    def get_keys(self):
        record = self.env["res.company"].browse(
            self.env.context.get("active_id"))
        directory = os.path.join(
            os.path.abspath(config["data_dir"]),
            "certificates",
            release.series,
            self.env.cr.dbname,
            record.facturae_cert_folder)
        file = base64.b64decode(record.facturae_cert_file)
        if tuple(map(int, cryptography.__version__.split("."))) < (3, 0):
            raise exceptions.UserError(_(
                "Cryptography version is not supported. Upgrade to 3.0.0 "
                "or greater."))
        try:
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            pfx_password = self.password
            pfx_password = bytes(pfx_password)
            p12 = pkcs12.load_key_and_certificates(
                file, pfx_password, backend=default_backend())
            vals = self._process_certificate_vals(record, p12, directory)
            record.write(vals)
        except Exception as e:
            if e.args:
                args = list(e.args)
            raise ValidationError(args[-1])

    def _process_certificate_vals(self, record, p12, directory):
        vals = {}
        with pfx_to_pem(p12, directory) as private_key:
            vals["facturae_cert_private_key"] = private_key
        with pfx_to_crt(p12, directory) as public_key:
            vals["facturae_cert_public_key"] = public_key
        certificate = p12[1]
        vals["facturae_cert_date_start"] = certificate.not_valid_before
        vals["facturae_cert_date_end"] = certificate.not_valid_after
        if not record.name:
            name = certificate.subject.get_attributes_for_oid(
                x509.NameOID.COMMON_NAME)
            if name:
                vals["facturae_cert_name"] = name[0].value
        return vals
