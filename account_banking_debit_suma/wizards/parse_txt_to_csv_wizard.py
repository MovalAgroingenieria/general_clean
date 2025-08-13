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
        ('TAX_OBJECT',   182, 40),
    ]

    FW_FIELDS = [
        ('ACCOUNTING_YEAR',   0,  4),
        ('BILLING_PERIOD',    4,  2),
        ('INVOICE_TYPE',      6,  1),
        ('OPERATION_CODE',    7,  3),
        ('BREAKDOWN_CODE',   10,  3),
        ('OP_DATE',          13,  8),
        ('CHARGE_YEAR',      21,  4),
        ('EXTERNAL_MUNICIPAL', 25,  3),
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
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self.order_id._name),
            ('res_id', '=', self.order_id.id),
            ('datas_fname', 'ilike', '.txt'),
        ])
        attachments = attachments.filtered(
            lambda a: (self.order_id.name or '') in (a.datas_fname or ''))
        if not attachments:
            raise UserError("No matching attachments found for the order.")
        pay_att = attachments[0]
        raw = base64.b64decode(pay_att.datas)
        pay_name = pay_att.datas_fname or 'pay.txt'
        pay_path = os.path.join(tmp, pay_name)
        with open(pay_path, 'wb') as f:
            f.write(raw)
        join_keys = self._build_join_keys(suma_path)
        base = (self.suma_filename or 'result').rsplit('.', 1)[0]
        out_name = '%s_joined.csv' % base
        out_path = os.path.join(tmp, out_name)
        matches, total, invoice_numbers = self._match_and_extract(
            pay_path, join_keys, out_path)
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
        for inv_ref in invoice_numbers:
            inv = self.env['account.invoice'].search(
                [('number', '=', inv_ref)], limit=1)
            if inv:
                inv.sudo().write({'suma_settlement': self.order_id.name})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _parse_fixed_width(self, line, schema):
        return {n: line[s:s+w] for n, s, w in schema}

    def _build_join_keys(self, path):
        keys = set()
        with open(path, 'rb') as f:
            for raw in f:
                text = raw.decode('latin1')
                if len(text) < max(s+w for _, s, w in self.FW_FIELDS):
                    continue
                rec = self._parse_fixed_width(text, self.FW_FIELDS)
                if rec['INVOICE_TYPE'] == 'V' and rec[
                        'OPERATION_CODE'] == 'ING' and rec[
                            'BREAKDOWN_CODE'] == 'ING':
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
        invoice_numbers = []
        with open(path, 'rb') as reg, open(out_path, 'wb') as out:
            writer = csv.writer(out, encoding='utf-8')
            writer.writerow(['JOIN_KEY', 'NAME', 'INVOICE', 'PRICE_EUR'])
            for raw in reg:
                text = raw.decode('latin1')
                if len(text) < max(s+w for _, s, w in self.REG_FIELDS):
                    continue
                hdr = text[:37]
                key = next((k for k in join_keys if k in hdr), None)
                if not key:
                    continue
                rec = self._parse_fixed_width(text, self.REG_FIELDS)
                name = rec['NAME'].rstrip()
                invoice = rec['TAX_OBJECT'].rstrip()
                cents = int(''.join(ch for ch in rec[
                    'AMOUNT_CENTS'] if ch.isdigit()) or 0)
                euros = cents / 100.0
                total += euros
                writer.writerow([key, name, invoice, "{:.2f}".format(
                    euros).replace('.', ',')])
                count += 1
                invoice_numbers.append(invoice)
        return count, total, invoice_numbers
