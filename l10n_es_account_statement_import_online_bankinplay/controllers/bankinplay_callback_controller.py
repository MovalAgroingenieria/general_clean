# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request


class BankinplayCallbackController(http.Controller):
    @http.route(
        '/webhook/bankinplay_callback', type='json', auth='public',
        methods=['POST'], csrf=False)
    def handle_bankinplay_callback(self, **kw):
        json_data = request.jsonrequest
        # Get JSON and check if its a Close reading, which are the only one
        # handled yet
        if ('responseId' in json_data and 'signature' in json_data and
                'triggered_event' in json_data and
                json_data['triggered_event'] == 'lectura_cierre'):
            import_statement = request.env['account.bank.statement'].sudo().\
                search([
                    ('bankinplay_responseid', '=', json_data['responseId']),
                    ('bankinplay_signature', '=', json_data['signature']),
                ])
            # If statement already created,
            if (import_statement):
                import_statement.journal_id.online_bank_statement_provider_id.\
                    _bankinplay_update_statement_data_after_callback(
                        import_statement, json_data['data'])
