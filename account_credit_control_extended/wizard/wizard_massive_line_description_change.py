# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from jinja2 import Template, TemplateError
from odoo import models, fields, _, api, exceptions
from datetime import datetime
import random


class WizardMassiveLineDescriptionChange(models.TransientModel):
    _name = 'wizard.massive.line.description.change'

    def _default_control_line_ids(self):
        active_ids = self.env.context.get('active_ids')
        return [(6, 0, active_ids)] if active_ids else []

    control_line_ids = fields.Many2many(
        string="Control Lines",
        comodel_name='credit.control.line',
        default=_default_control_line_ids,
    )

    line_description_template = fields.Text(
        string="Line description Jinja Template",
        default="""
            {% if object.invoice_id -%}
                {%- for line in object.invoice_id.invoice_line_ids -%}
                    {{ line.name }}{% if not loop.last %}, {% endif %}
                {%- endfor -%}
            {%- endif %}
        """,
    )

    line_description_template_resolved = fields.Text(
        string='Template resolved',
        readonly=True,
        help='The template after resolve variables using random item.',
    )

    def _get_random_line(self):
        line = ''
        line_ids = self.env['credit.control.line'].search(
            [], limit=1000).ids
        if len(line_ids) > 0:
            random_line_id = random.choice(line_ids)
            line = self.env['credit.control.line'].browse(
                random_line_id)
        else:
            raise exceptions.ValidationError(_('No line found'))
        return line

    @api.multi
    def action_resolve_template(self):
        self.ensure_one()
        template = line = message = ''
        if self.line_description_template:
            template = Template(self.line_description_template)
            line = self._get_random_line()
            try:
                message = template.render(
                    object=line, datetime=datetime)
            except TemplateError as err:
                raise exceptions.ValidationError(
                    _('Error resolving template: {}'.format(err.message)))
        if message:
            self.line_description_template_resolved = message
        return {
            "type": "ir.actions.do_nothing",
        }

    def generate_credit_lines_description(self):
        template = Template(self.line_description_template)
        for line in self.control_line_ids:
            try:
                line.description_html = template.render(
                    object=line, datetime=datetime)
            except TemplateError:
                pass