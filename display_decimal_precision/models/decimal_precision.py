# 2023 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools


class DecimalPrecision(models.Model):
    _inherit = 'decimal.precision'

    display_digits = fields.Integer(
        string='Display Digits',
        required=True,)

    @api.model
    @tools.ormcache('application')
    def display_precision_get(self, application):
        self.flush(['name', 'digits'])
        self.env.cr.execute(
            'SELECT display_digits FROM decimal_precision WHERE name=%s',
            (application,))
        res = self.env.cr.fetchone()
        return res[0] if res else 2

    @staticmethod
    def get_display_precision(env, application):
        res = 2
        dp = env['decimal.precision']
        res = dp.display_precision_get(application)
        return 16, res
