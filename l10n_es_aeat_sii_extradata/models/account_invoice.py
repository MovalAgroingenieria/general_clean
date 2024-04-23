# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree
from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # Overwrite parent method
    @api.multi
    def _get_sii_in_taxes(self):
        self.ensure_one()
        taxes_dict = {}
        taxes_sfrs = self._get_sii_taxes_map(['SFRS'])
        taxes_sfrsa = self._get_sii_taxes_map(['SFRSA'])
        taxes_sfrisp = self._get_sii_taxes_map(['SFRISP'])
        taxes_sfrns = self._get_sii_taxes_map(['SFRNS'])
        taxes_sfrnd = self._get_sii_taxes_map(['SFRND'])

        taxes_not_in_total = self._get_sii_taxes_map(['NotIncludedInTotal'])
        base_not_in_total = self._get_sii_taxes_map(['BaseNotIncludedInTotal'])
        tax_amount = 0.0
        # Check if refund type is 'By differences'. Negative amounts!
        sign = self._get_sii_sign()
        for tax_line in self.tax_line_ids:
            tax = tax_line.tax_id

            if tax in (taxes_not_in_total + base_not_in_total):
                amount = (
                    tax_line.base if tax in base_not_in_total else self.amount_untaxed
                )
                if self.currency_id != self.company_id.currency_id:
                    amount = self.currency_id._compute(
                        self.currency_id,
                        self.company_id.currency_id,
                        amount,
                    )
            if tax in taxes_sfrisp:
                isp_dict = taxes_dict.setdefault(
                    'InversionSujetoPasivo', {'DetalleIVA': []},
                )
                isp_dict['DetalleIVA'].append(
                    self._get_sii_tax_dict(tax_line, sign),
                )
                tax_amount += abs(round(tax_line.amount_company, 2))
            elif tax in taxes_sfrs:
                sfrs_dict = taxes_dict.setdefault(
                    'DesgloseIVA', {'DetalleIVA': []},
                )
                sfrs_dict['DetalleIVA'].append(
                    self._get_sii_tax_dict(tax_line, sign),
                )
                tax_amount += round(tax_line.amount_company, 2)
            elif tax in taxes_sfrns:
                sfrns_dict = taxes_dict.setdefault(
                    'DesgloseIVA', {'DetalleIVA': []},
                )
                sfrns_dict['DetalleIVA'].append({
                    'BaseImponible': sign * tax_line.base_company,
                })
            # Only modification with respect to the parent method
            elif tax in taxes_sfrnd:
                pass
            else:
                continue
            tax_dict = self._get_sii_tax_dict(tax_line, sign)
            if tax in taxes_sfrns:
                tax_dict.pop("TipoImpositivo")
                tax_dict.pop("CuotaSoportada")
            elif tax in taxes_sfrsa:
                sfrsa_dict = taxes_dict.setdefault(
                    'DesgloseIVA', {'DetalleIVA': []},
                )
                tax_dict = self._get_sii_tax_dict(tax_line, sign)
                tax_dict['PorcentCompensacionREAGYP'] = tax_dict.pop(
                    'TipoImpositivo'
                )
                tax_dict['ImporteCompensacionREAGYP'] = tax_dict.pop(
                    'CuotaSoportada'
                )
                sfrsa_dict['DetalleIVA'].append(tax_dict)
            elif tax in taxes_sfrnd:
                sfrnd_dict = taxes_dict.setdefault(
                    'DesgloseIVA', {'DetalleIVA': []},
                )
                sfrnd_dict['DetalleIVA'].append(
                    self._get_sii_tax_dict(tax_line, sign),
                )
        return taxes_dict, tax_amount

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(AccountInvoice, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        is_portal_user = self.env.user.has_group('base.group_portal')
        if not is_portal_user:
            return res
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='invoice_jobs_ids']"):
                parent = node.getparent()
                parent.remove(node)
            res['arch'] = etree.tostring(doc)
        return res
