# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models, tools


class MailMail(models.Model):
    _inherit = ['mail.mail']

    @api.multi
    def send_get_email_dict(self, partner=None):
        res = super(MailMail, self).send_get_email_dict(partner)
        base_url = self.env['ir.config_parameter'].get_param(
            'web.base.url').rstrip('/')
        # Solution for invidual mail multi-recipient and encoding
        email_to_raw = res.get('email_to')
        email_to_coded = email_to_raw[0].encode('utf-8')
        if '<' in email_to_coded:
            only_emails_raw = email_to_coded.split('<')[1]
            only_emails = only_emails_raw.rstrip('>').replace(';', ',')
        else:
            only_emails = email_to_coded.replace(';', ',')
        emails = tools.email_split(only_emails)
        res['email_to'] = emails
        # Solution for mass_mailing multi-recipient and encoding
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
