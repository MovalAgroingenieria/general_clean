# -*- coding: utf-8 -*-
# 2023 Moval Agroingeniería
# © 2015 Tecon
# © 2015 Omar Castiñeira (Comunitea)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, exceptions, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _default_facturae_cert_company_id(self):
        company_id = self.id
        return company_id

    facturae_cert_state = fields.Selection(
        selection=[("draft", "Draft"), ("active", "Active")],
        string="State",
        default="draft")
    facturae_cert_file = fields.Binary(string="File", required=True)
    facturae_cert_folder = fields.Char(string="Folder Name", required=True)
    facturae_cert_date_start = fields.Date(string="Start Date")
    facturae_cert_date_end = fields.Date(string="End Date")
    facturae_cert_public_key = fields.Char(string="Public Key", readonly=True)
    facturae_cert_private_key = fields.Char(
        string="Private Key",
        readonly=True)
    facturae_cert_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        store=True,
        default=_default_facturae_cert_company_id,
        compute="_compute_facturae_cert_company_id")

    @api.multi
    def _compute_facturae_cert_company_id(self):
        for record in self:
            record.facturae_cert_company_id = record.id

    def facturae_cert_load_password_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Insert Password"),
            "res_model": "l10n.es.facturae.certificate.password",
            "view_mode": "form",
            "views": [(False, "form")],
            "target": "new",
        }

    def facturae_cert_action_active(self):
        self.ensure_one()
        self.facturae_cert_state = "active"

    def facturae_cert_action_draft(self):
        self.ensure_one()
        self.facturae_cert_state = "draft"

    def facturae_cert_get_certificates(self, company=False):
        public_crt = False
        private_key = False
        if not company:
            company = self.env.user.company_id
        today = fields.Date.today()
        company_with_certificate = self.search(
            [
                ("facturae_cert_company_id", "=", company.id),
                ("facturae_cert_public_key", "!=", False),
                ("facturae_cert_private_key", "!=", False),
                "|",
                ("facturae_cert_date_start", "=", False),
                ("facturae_cert_date_start", "<=", today),
                "|",
                ("facturae_cert_date_end", "=", False),
                ("facturae_cert_date_end", ">=", today),
                ("facturae_cert_state", "=", "active"),
            ],
            limit=1,
        )
        if company_with_certificate:
            public_crt = company_with_certificate.facturae_cert_public_key
            private_key = company_with_certificate.facturae_cert_private_key
        if not public_crt or not private_key:
            raise exceptions.UserError(_("Error! There aren't certificates."))
        return public_crt, private_key
