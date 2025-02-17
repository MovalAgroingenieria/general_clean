# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ResLetterMailWizard(models.TransientModel):
    _name = 'res.letter.mail.wizard'

    def _default_optional_text(self):
        text = _('Notice of registration. Report attached.')
        return text

    optional_text = fields.Text(
        string='Optional Text',
        default=_default_optional_text,
        help='Text that will be included in the email.')

    @api.multi
    def action_send_mails(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        registres = self.env['res.letter'].browse(active_ids)
        template = self.env.ref(
            'crm_lettermgmt.email_template_res_letter', False)
        if not template:
            return True
        for registre in registres:
            # Data
            sender = registre.sender_partner_id
            sender_email = sender.email
            # Report
            pdf_content = self.env['report'].get_pdf(
                [registre.id], 'crm_lettermgmt.template_res_letter_report')
            document_name = '{}.pdf'.format(
                registre.number.replace('/', '_'))
            pdf_base64 = pdf_content.encode('base64')
            attachment = self.env['ir.attachment'].create({
                'res_model': 'res.letter',
                'res_id': registre.id,
                'name': document_name,
                'datas': pdf_base64,
                'datas_fname': document_name,
                'mimetype': 'application/pdf'})
            # Email
            ctx = {
                'default_model': 'res.letter',
                'default_res_id': registre.id,
                'optional_text': self.optional_text,
                'partner_to_sent': sender,
                'partner_email': sender_email,
                'default_attachment_ids': [(4, attachment.id)]}
            mail = template.with_context(ctx).generate_email(registre.id)
            body_html = mail.get('body_html', '')
            template.with_context(ctx).send_mail(registre.id, force_send=True)
            # Log
            registre.message_post(
                body=body_html,
                subject=mail.get('subject', ''),
                message_type='comment',
                attachment_ids=[attachment.id])
        return True
