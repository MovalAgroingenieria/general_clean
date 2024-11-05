# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class RatingParentMixin(models.AbstractModel):
    _inherit = 'rating.parent.mixin'
    rating_ids = fields.One2many(
        groups='base.group_user,'
        'project_limited_access.group_portal_project_user',
    )


class RatingMixin(models.AbstractModel):
    _inherit = 'rating.mixin'

    rating_ids = fields.One2many(
        groups='base.group_user,'
        'project_limited_access.group_portal_project_user',
    )

    rating_last_value = fields.Float(
        groups='base.group_user,'
        'project_limited_access.group_portal_project_user',
    )

    rating_last_feedback = fields.Text(
        groups='base.group_user,'
        'project_limited_access.group_portal_project_user',
    )

    rating_last_image = fields.Binary(
        groups='base.group_user,'
        'project_limited_access.group_portal_project_user',
    )
