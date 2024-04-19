# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
import logging
import re
from datetime import datetime

import pytz

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class OnlineBankStatementProviderBankinplay(models.Model):
    _inherit = 'online.bank.statement.provider'

    bankinplay_date_field = fields.Selection(
        [
            ('operation_date', 'Operation Date'),
            ('value_date', 'Value Date'),
        ],
        string='Bankinplay Date Field',
        default='operation_date',
        help='Select the Bankinplay date field that will be used for '
        'the Odoo bank statement line date.',
    )

    bankinplay_end_point = fields.Char(
        string='Bankinplay endpoint',
        default='execution_date',
        help='Where callback webhook is gonna be setted, just in case don\'t. '
        'want to use the default controller functions',
    )

    @api.model
    def _get_available_services(self):
        '''Each provider model must register its service.'''
        return super()._get_available_services() + [
            ('bankinplay', 'BankInPlay.com'),
        ]

    def _obtain_statement_data(self, date_since, date_until):
        '''Check wether called for bankinplay servide, otherwise pass the
           buck.'''
        self.ensure_one()
        if self.service != 'bankinplay':  # pragma: no cover
            return super()._obtain_statement_data(
                date_since,
                date_until,
            )
        return self._bankinplay_obtain_statement_data(date_since, date_until)

    def _bankinplay_obtain_statement_data(self, date_since, date_until):
        '''Create Callbacks to being processed afterwards.'''
        self.ensure_one()
        _logger.debug(
            _('Bankinplay obtain statement data for journal %s from %s to %s'),
            self.journal_id.name,
            date_since,
            date_until,
        )
        response_data = self._bankinplay_retrieve_data(date_since, date_until)
        return [], response_data

    def _bankinplay_update_statement_data_after_callback(
            self, bank_statement, data):
        '''Translate information from Bankinplay to Odoo bank statement
           lines.'''
        self.ensure_one()
        all_transactions = self._bankinplay_get_transactions_from_data(
            data)
        self._create_or_update_statement(
            (all_transactions, {}), bank_statement.bankinplay_date_since,
            bank_statement.bankinplay_date_until)
        bank_statement.balance_end_real = bank_statement.balance_end

    def _bankinplay_retrieve_data(self, date_since, date_until):
        '''Fill buffer with data from Bankinplay.

        Register a method for retrieval of transactions which will be processed
        later by the callback action by adding the statement lines.
        '''
        response_data = {}
        interface_model = self.env['bankinplay.interface']
        access_data = interface_model._login(self.username, self.password)
        interface_model._set_access_account(access_data, self.account_number)
        response_data = interface_model._set_close_movements_callback(
            access_data, date_since, date_until)
        return response_data

    def _bankinplay_get_transactions_from_data(self, data):
        '''Translate information from Bankinplay to statement line vals.'''
        interface_model = self.env['bankinplay.interface']
        access_data = interface_model._login(self.username, self.password)
        transactions_decrypted = interface_model._decrypt_bankinplay_data(
            data, access_data['username'], access_data['password']).get(
            'results', [])
        sequence = 0
        all_transactions = []
        for transaction_decrypted in transactions_decrypted:
            transaction_line = self._bankinplay_get_transaction_vals(
                transaction_decrypted, sequence)
            all_transactions.append(transaction_line)
            sequence += 1
        return all_transactions

    def _bankinplay_get_transaction_vals(self, transaction, sequence):
        '''Translate information from Bankinplay to statement line vals.'''
        date = self._bankinplay_get_transaction_datetime(transaction)
        ref = transaction.get('descripcion')
        amount = transaction.get('importeAbsoluto', 0)
        amount_multiplier = transaction.get('signo', 'Cobro')
        if (amount_multiplier != 'Cobro'):
            amount *= -1
        vals_line = {
            'sequence': sequence,
            'date': date,
            'ref': re.sub(' +', ' ', ref) or '/',
            'unique_import_id': str(transaction['id']),
            'amount': amount,
            'raw_data': json.dumps(transaction),
        }
        return vals_line

    def _bankinplay_get_transaction_datetime(self, transaction):
        '''Get execution datetime for a transaction.

        Odoo often names variables containing date and time just xxx_date or
        date_xxx. We try to avoid this misleading naming by using datetime as
        much for variables and fields of type datetime.
        '''
        if self.bankinplay_date_field == 'value_date':
            datetime_str = transaction.get('fechaValor')
        else:
            datetime_str = transaction.get('fechaOperacion')
        return self._bankinplay_datetime_from_string(datetime_str)

    def _bankinplay_datetime_from_string(self, datetime_str):
        '''Dates in Bankinplay are expressed in UTC, so we need to convert them
        to supplied tz for proper classification.
        '''
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
        dt = dt.replace(tzinfo=pytz.utc).astimezone(
            pytz.timezone(self.tz or "utc"))
        return dt.replace(tzinfo=None)
