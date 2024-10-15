# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    # image = fields.Binary(
    #     string='Image',
    #     attachment=True,
    #     )

    image= fields.Image(
        string='Image (1920 x 1920)',
        max_width=1920,
        max_height=1920,)

    image_1024 = fields.Image(
        string='Aerial Image (1024 x 1024)',
        max_width=1024,
        max_height=1024,
        store=True,
        related='image',)

    image_512 = fields.Image(
        string='Image (512 x 512)',
        max_width=512,
        max_height=512,
        store=True,
        related='image',)

    image_256 = fields.Image(
        string='Image (256 x 256)',
        max_width=256,
        max_height=256,
        store=True,
        related='image',)

    image_128 = fields.Image(
        string='Image (128 x 52)',
        max_width=128,
        max_height=52,
        store=True,
        related='image',)

    image_1920 = fields.Image(
        string='Image (zoom)',
        related='image',)
