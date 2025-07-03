# © 2025 Moval Agroingeniería
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class MaterialComponentLine(models.Model):
    _name = 'material.component.line'
    _description = 'Material Component Line'

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
    )

    material_id = fields.Many2one(
        comodel_name='product.material',
        string='Material',
        required=True,
    )

    submaterial_id = fields.Many2one(
        comodel_name='product.submaterial',
        string='Submaterial',
        required=True,
    )

    submaterial_type_id = fields.Many2one(
        comodel_name='submaterial.type',
        string='Submaterial Type',
        required=True,
    )

    weight_grams = fields.Float(
        string='Weight (g)',
        digits=(16, 2),
    )

    @api.onchange('submaterial_type_id')
    def _onchange_type_id(self):
        for line in self:
            if line.submaterial_type_id:
                line.submaterial_id = line.submaterial_type_id.submaterial_id
                line.material_id = \
                    line.submaterial_type_id.submaterial_id.material_id
            else:
                line.submaterial_id = False
                line.material_id = False
