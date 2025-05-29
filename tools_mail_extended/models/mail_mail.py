# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo import tools


class MailMail(models.Model):
    _inherit = 'mail.mail'

    @api.multi
    def send_get_mail_to(self, partner=None):
        self.ensure_one()
        if partner:
            email_to = tools.email_split_and_format(partner.email)
        else:
            email_to = tools.email_split_and_format(self.email_to)
        return email_to
