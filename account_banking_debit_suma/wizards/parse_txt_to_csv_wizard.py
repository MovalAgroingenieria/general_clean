# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import tempfile
import base64
import unicodecsv as csv
from odoo import models, fields, api
from odoo.exceptions import UserError


class TxtToCsvWizard(models.TransientModel):
    _name = 'txt.to.csv.wizard'
    _description = 'TXT to CSV Wizard'

    suma_file = fields.Binary(
        string='SUMA TXT',
        required=True,
    )
    suma_filename = fields.Char(
        string='SUMA Filename',
    )

    order_id = fields.Many2one(
        'account.payment.order',
        string='Payment Order',
        domain="[('payment_mode_name','=','Liquidaciones Suma')]",
        required=True,
    )

    csv_file = fields.Binary(
        string='CSV File',
        readonly=True,
    )
    csv_filename = fields.Char(
        string='CSV Filename',
        readonly=True,
    )
    matches_count = fields.Integer(
        string='Matches',
        readonly=True,
    )
    total_amount = fields.Float(
        string='Total Amount',
        readonly=True,
    )

    REG_FIELDS = [
        ('NAME',         38, 60),
        ('AMOUNT_CENTS', 161, 10),
        ('TAX_OBJECT',  182, 40),
    ]

    FW_FIELDS = [
        ('ACCOUNTING_YEAR',   0,  4),
        ('BILLING_PERIOD',    4,  2),
        ('INVOICE_TYPE',      6,  1),
        ('OPERATION_CODE',    7,  3),
        ('BREAKDOWN_CODE',   10,  3),
        ('OP_DATE',          13,  8),
        ('CHARGE_YEAR',      21,  4),
        ('EXTERNAL_MUNICIPAL', 25, 3),
        ('CONCEPT_CODE',     28,  2),
        ('ISSUE_CODE',       30,  2),
        ('ORGANISM_CODE',    32,  1),
        ('VALUE_TYPE',       33,  1),
        ('LIST_REF',         34,  6),
        ('PRINCIPAL',        41, 13),
        ('COUNTER_YEAR',     54,  4),
        ('INTERNAL_REF',     58, 15),
        ('COMMON_FILLER',    73, 15),
    ]

    @api.multi
    def action_parse_and_generate(self):
        self.ensure_one()
        tmp = tempfile.gettempdir()
        suma_path = os.path.join(tmp, self.suma_filename or 'suma.txt')
        with open(suma_path, 'wb') as f:
            f.write(base64.b64decode(self.suma_file))
        attachment_obj = self.env['ir.attachment']
        domain = [
            ('res_model', '=', self.order_id._name),
            ('res_id', '=', self.order_id.id),
            ('datas_fname', 'ilike', '.txt'),
        ]
        attachments = attachment_obj.search(domain)
        pay_name_key = self.order_id.name or ''
        attachments = attachments.filtered(
            lambda a: pay_name_key in (a.datas_fname or ''))
        if not attachments:
            raise UserError("There's no TXT file related to this PAY.")
        att = attachments[0]
        raw_bytes = base64.b64decode(att.datas)
        pay_name = att.datas_fname
        pay_path = os.path.join(tmp, pay_name)
        with open(pay_path, 'wb') as f:
            f.write(raw_bytes)
        join_keys = self._build_join_keys(suma_path)
        base = (self.suma_filename or 'result').rsplit('.', 1)[0]
        out_name = '%s_suma.csv' % base
        out_path = os.path.join(tmp, out_name)
        matches, total = self._match_and_extract(pay_path, join_keys, out_path)
        with open(out_path, 'rb') as f:
            csv_data = f.read()
        csv_b64 = base64.b64encode(csv_data)
        self.env['ir.attachment'].create({
            'name': out_name,
            'datas': csv_b64,
            'datas_fname': out_name,
            'res_model': self.order_id._name,
            'res_id': self.order_id.id,
            'type': 'binary',
        })
        self.csv_file = csv_b64
        self.csv_filename = out_name
        self.matches_count = matches
        self.total_amount = total

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _parse_fixed_width(self, text_line, schema):
        return {
            name: text_line[
                start:start+width] for name, start, width in schema}

    def _build_join_keys(self, path):
        keys = set()
        with open(path, 'rb') as f:
            for raw in f:
                line = raw.decode('latin1')
                if len(line) < max(s + w for _, s, w in self.FW_FIELDS):
                    continue
                rec = {n: line[s:s + w] for n, s, w in self.FW_FIELDS}
                if (rec['INVOICE_TYPE'] == 'V' and
                    rec['OPERATION_CODE'] == 'ING' and
                        rec['BREAKDOWN_CODE'] == 'ING'):
                    keys.add(''.join([
                        rec['ORGANISM_CODE'],
                        rec['VALUE_TYPE'],
                        rec['LIST_REF'],
                        rec['INTERNAL_REF'],
                    ]))
        return keys

    def _match_and_extract(self, path, join_keys, out_path):
        count = 0
        total = 0.0
        with open(path, 'rb') as reg, open(out_path, 'wb') as out:
            writer = csv.writer(out, encoding='utf-8')
            writer.writerow(['JOIN_KEY', 'NAME', 'INVOICE', 'PRICE_EUR'])
            for raw in reg:
                line = raw.decode('latin1')
                if len(line) < max(s + w for _, s, w in self.REG_FIELDS):
                    continue
                hdr = line[:37]
                key = next((k for k in join_keys if k in hdr), None)
                if not key:
                    continue
                rec = {n: line[s:s + w] for n, s, w in self.REG_FIELDS}
                name = rec['NAME'].rstrip()
                invoice = rec['TAX_OBJECT'].rstrip()
                cents = int(
                    ''.join(ch for ch in rec['AMOUNT_CENTS'] if ch.isdigit()))
                euros = cents / 100.0
                total += euros
                price = "{:.2f} €".format(euros).replace('.', ',')
                writer.writerow([key, name, invoice, price])
                count += 1
        return count, total
