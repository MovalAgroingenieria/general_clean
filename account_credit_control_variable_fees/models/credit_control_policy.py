# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields, api


class CreditControlPolicyLevel(models.Model):
    _inherit = "credit.control.policy.level"

    variable_fees_percentage = fields.Integer(
        string="Variable fees (%)",
        help="The percentage of increase in debt at this level.")

    custom_text_after_variable_fees = fields.Html(
        string='Custom Message after variable fees',
        translate=True,
        help="The message to explain the reason for the increase in debt.")

    _sql_constraints = [
        ('valid_variable_fees_percentage',
         'CHECK (variable_fees_percentage >= 0)',
         'The variable fees percentage must be a value zero or positive.'),
        ]


class CreditControlLine(models.Model):
    _inherit = "credit.control.line"

    variable_fees_percentage = fields.Integer(
        compute="_compute_variable_fees_percentage")

    variable_fees = fields.Float(
        string="Variable fees",
        compute="_compute_variable_fees")

    total_amount_with_fees = fields.Float(
        string="Total amount",
        compute="_compute_total_amount_with_fees")

    @api.multi
    def _compute_variable_fees_percentage(self):
        for record in self:
            record.variable_fees_percentage = \
                record.policy_level_id.variable_fees_percentage

    @api.depends('variable_fees_percentage', 'balance_due')
    def _compute_variable_fees(self):
        for record in self:
            variable_fees = 0
            if record.variable_fees_percentage > 0 and record.balance_due > 0:
                factor = float(record.variable_fees_percentage) / 100
                variable_fees = factor * record.balance_due
            record.variable_fees = variable_fees

    @api.depends('variable_fees', 'balance_due')
    def _compute_total_amount_with_fees(self):
        for record in self:
            record.total_amount_with_fees = \
                record.variable_fees + record.balance_due


class CreditCommunication(models.TransientModel):
    _inherit = "credit.control.communication"

    variable_fees_percentage = fields.Integer(
        compute="_compute_variable_fees_percentage")

    @api.multi
    def _compute_variable_fees_percentage(self):
        for record in self:
            if len(record.credit_control_line_ids) == 1:
                record.variable_fees_percentage = \
                    record.current_policy_level.variable_fees_percentage
