# -*- coding: utf-8 -*-
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from jinja2 import Template, TemplateError


class CommunicationWizard(models.TransientModel):
    _name = "communication.wizard"
    _description = "Wizard to edit communication field"

    communication_template = fields.Char(
        string="Communication template",
        help="Template with jinja2 variables for Communication fields.\nIt "
             "will be cut to 140 characters after solving the variables.")

    @api.multi
    def edit_communication_action(self, context):
        active_ids = context.get('active_ids')
        if not active_ids:
            raise ValidationError(_("There are no items selected."))

        raw_template = False
        if self.communication_template:
            raw_template = Template(self.communication_template)

        for active_id in active_ids:
            payment_order = self.env['account.payment.order'].browse(active_id)
            if payment_order.bank_line_ids:
                raise ValidationError(
                    _("Bank lines have already been generated. Cancel payments"
                      " before edit the communication field."))
            if payment_order.payment_line_ids:
                for payment_line in payment_order.payment_line_ids:
                    invoice = False
                    new_communication = False
                    if payment_line.invoice_id:
                        invoice = payment_line.invoice_id
                    if invoice:
                        try:
                            new_communication = raw_template.render(
                                payment_order=payment_order,
                                payment_line=payment_line,
                                invoice=invoice)
                        except TemplateError as err:
                            raise ValidationError(
                                _('Error resolving template: '
                                  '{}'.format(err.message)))
                    if new_communication:
                        new_communication = new_communication[:140]
                        payment_line.communication = new_communication
