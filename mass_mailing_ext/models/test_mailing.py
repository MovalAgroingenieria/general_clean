# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools


class TestMassMailing(models.TransientModel):
    _inherit = 'mail.mass_mailing.test'

    @api.multi
    def send_mail_test(self):
        self.ensure_one()
        mails = self.env['mail.mail']
        mailing = self.mass_mailing_id
        email_to_raw = self.email_to
        email_to_coded = email_to_raw.encode('utf-8')
        if '<' in email_to_coded:
            only_emails_raw = email_to_coded.split('<')[1]
            only_emails = only_emails_raw.rstrip('>').replace(';', ',')
        else:
            only_emails = email_to_coded.replace(';', ',')
        emails = tools.email_split(only_emails)
        test_emails = emails
        for test_mail in test_emails:
            mailing.write({'body_html': self.env[
                'mail.template']._replace_local_links(mailing.body_html)})
            mail_values = {
                'email_from': mailing.email_from,
                'reply_to': mailing.reply_to,
                'email_to': test_mail,
                'subject': mailing.name,
                'body_html': tools.html_sanitize(
                    mailing.body_html, sanitize_attributes=True,
                    sanitize_style=True, strip_classes=True),
                'notification': True,
                'mailing_id': mailing.id,
                'attachment_ids':
                    [(4, attachment.id)
                     for attachment in mailing.attachment_ids],
            }
            mail = self.env['mail.mail'].create(mail_values)
            mails |= mail
        mails.send()
        return True
