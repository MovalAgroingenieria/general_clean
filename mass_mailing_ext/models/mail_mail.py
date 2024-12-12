# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, tools


class MailMail(models.Model):
    _inherit = ['mail.mail']

    @api.multi
    def send_get_email_dict(self, partner=None):
        self.ensure_one()
        body = self.send_get_mail_body(partner=partner)
        body_alternative = tools.html2plaintext(body)
        res = {
            'body': body,
            'body_alternative': body_alternative,
            'email_to': self.send_get_mail_to(partner=partner),
        }
        base_url = self.env['ir.config_parameter'].get_param(
            'web.base.url').rstrip('/')
        if self.mailing_id and res.get('body') and res.get('email_to'):
            original_email_to = res.get('email_to')[0]
            modified_email_to = original_email_to.encode('utf-8')
            emails = tools.email_split(modified_email_to)
            email_to = emails and emails[0] or False
            unsubscribe_url = self._get_unsubscribe_url(email_to)
            link_to_replace = base_url + '/unsubscribe_from_list'
            if link_to_replace in res['body']:
                res['body'] = res['body'].replace(
                    link_to_replace,
                    unsubscribe_url if unsubscribe_url else '#')
        return res
