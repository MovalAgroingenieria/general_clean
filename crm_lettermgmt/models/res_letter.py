# -*- coding: utf-8 -*-
# © 2016 Iván Todorovich <ivan.todorovich@gmail.com>
# © 2015 Holger Brunn <hbrunn@therp.nl>
# © 2009 Sandy Carter <sandy.carter@savoirfairelinux.com>
# © 2009 Parthiv Patel, Tech Receptives
# 2020 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
from odoo import models, fields, api


class ResLetter(models.Model):
    """A register class to log all movements regarding letters"""
    _name = 'res.letter'
    _description = "Log of Letter Movements"
    _inherit = 'mail.thread'

    number = fields.Char(
        help="Auto Generated Number of letter.",
        default="/")

    name = fields.Text(
        string='Subject',
        help="Subject of letter.")

    move = fields.Selection(
        [('in', 'IN'), ('out', 'OUT')],
        help="Incoming or Outgoing Letter.",
        readonly=True,
        default=lambda self: self.env.context.get('move', 'in'))

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('rec', 'Received'),
            ('rec_bad', 'Received Damage'),
            ('rec_ret', 'Received But Returned'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
        help="""
            * Draft: not confirmed yet.\n
            * Sent: has been sent, can't be modified anymore.\n
            * Received: has arrived.\n
            * Received Damage: has been received with damages.\n
            * Received But Returned: has been received but returned.\n
            * Cancel: has been cancelled, can't be sent anymore."""
        )

    date = fields.Date(
        string='Letter Date',
        help='The letter\'s date.',
        default=fields.Date.today)

    snd_date = fields.Date(
        string='Sent Date',
        help='The date the letter was sent.')

    rec_date = fields.Date(
        string='Received Date',
        help='The date the letter was received.')

    document_date = fields.Date(
        string='Document Date',
        help='The date of the document itself.')

    def default_recipient(self):
        move_type = self.env.context.get('move', False)
        if move_type == 'in':
            return self.env.user.company_id.partner_id

    def default_sender(self):
        move_type = self.env.context.get('move', False)
        if move_type == 'out':
            return self.env.user.company_id.partner_id

    recipient_partner_id = fields.Many2one(
        'res.partner',
        string='Recipient',
        track_visibility='onchange',
        default=default_recipient)

    sender_partner_id = fields.Many2one(
        'res.partner',
        string='Sender',
        track_visibility='onchange',
        default=default_sender)

    note = fields.Text(
        string='Delivery Notes',
        help='Indications for the delivery officer.')

    channel_id = fields.Many2one(
        'letter.channel',
        string="Channel",
        help='Sent / Receive Source')

    category_ids = fields.Many2many(
        'letter.category',
        string="Tags",
        help="Classification of Document.")

    folder_id = fields.Many2one(
        'letter.folder',
        string='Folder',
        help='Folder which contains letter.')

    type_id = fields.Many2one(
        'letter.type',
        string="Type",
        help="Type of Letter, Depending upon size.")

    # weight = fields.Float(help='Weight (in KG)')
    # size = fields.Char(help='Size of the package.')

    track_ref = fields.Char(
        string='Tracking Reference',
        help="Reference Number used for Tracking.")

    orig_ref = fields.Char(
        string='Original Reference',
        help="Reference Number at Origin.")

    expeditor_ref = fields.Char(
        string='Expeditor Reference',
        help="Reference Number used by Expeditor.")

    parent_id = fields.Many2one(
        'res.letter',
        string='Parent',
        groups='crm_lettermgmt.group_letter_thread')

    child_line = fields.One2many(
        'res.letter',
        'parent_id',
        string='Letter Lines',
        groups='crm_lettermgmt.group_letter_thread')

    reassignment_ids = fields.One2many(
        'letter.reassignment',
        'letter_id',
        string='Reassignment lines',
        help='Reassignment users and comments',
        groups='crm_lettermgmt.group_letter_reasignment')

    res_letter_attachment_ids = fields.One2many(
        string="Attachments",
        comodel_name="ir.attachment",
        compute="_compute_res_letter_attachment_ids")

    @api.multi
    def _compute_res_letter_attachment_ids(self):
        self.res_letter_attachment_ids = \
            self.env['ir.attachment'].search(
                [('res_model', '=', self._name), ('res_id', '=', self.id)])

    @api.multi
    def write(self, vals):
        if 'date' in vals and str(vals['date']) != fields.Date.today():
            move_type = self.move
            date_obj = datetime.datetime.strptime(
                str(vals['date']), '%Y-%m-%d')
            sequence_obj = self.env['ir.sequence'].search(
                [('code', '=', ('%s.letter' % move_type))])
            seq_len = sequence_obj.padding
            prefix_raw = str(sequence_obj.prefix)
            prefix = self._recompute_prefix(prefix_raw, date_obj)
            current_number = self.number[-seq_len:]
            number = prefix + current_number
            vals.update({'number': number})
        return super(ResLetter, self).write(vals)

    @api.model
    def create(self, vals):
        if ('number' not in vals) or (vals.get('number') in ('/', False)):
            sequence = self.env['ir.sequence']
            move_type = vals.get('move', self.env.context.get(
                'default_move', self.env.context.get('move', 'in')))
        # Use register's date for sequence number instead of today
        if ('date' in vals) and str(vals.get('date')) != fields.Date.today():
            date_obj = datetime.datetime.strptime(
                str(vals.get('date')), '%Y-%m-%d')
            sequence_obj = self.env['ir.sequence'].search(
                [('code', '=', ('%s.letter' % move_type))])
            next_num = str(sequence_obj.sudo().number_next_actual).zfill(
                    sequence_obj.padding)
            if sequence_obj.use_date_range:
                for date_range in sequence_obj.date_range_ids:
                    date_from = datetime.datetime.strptime(
                        date_range.date_from, '%Y-%m-%d')
                    date_to = datetime.datetime.strptime(
                        date_range.date_to, '%Y-%m-%d')
                    if date_from <= date_obj <= date_to:
                        next_num = str(date_range.number_next_actual).zfill(
                            sequence_obj.padding)
                        increased_seq_num = date_range.number_next_actual + 1
                        date_range.sudo().write(
                            {'number_next_actual': increased_seq_num})
                        break
            prefix_raw = str(sequence_obj.prefix)
            prefix = self._recompute_prefix(prefix_raw, date_obj)
            number = prefix + next_num
            vals['number'] = number
        else:
            vals['number'] = sequence.sudo().next_by_code(
                '%s.letter' % move_type)
        return super(ResLetter, self).create(vals)

    def _recompute_prefix(self, prefix_raw, date_obj):
        prefix = prefix_raw.replace(
            '%(year)s', str(date_obj.year)).replace(
            '%(y)s', '{:02d}'.format(int(date_obj.strftime("%y")))).replace(
            '%(month)s', '{:02d}'.format(date_obj.month)).replace(
            '%(day)s', '{:02d}'.format(date_obj.day)).replace(
            '%(weekday)s', '{:02d}'.format(date_obj.weekday())).replace(
            '%(woy)s', '{:02d}'.format(int(date_obj.strftime("%W")))).replace(
            '%(doy)s', '{:02d}'.format(int(date_obj.strftime("%j")))).replace(
            '%(h24)s', '00').replace('%(h12)s', '00').replace(
            '%(min)s', '00').replace('%(sec)s', '00')
        return prefix

    @api.one
    def action_cancel(self):
        """ Put the state of the letter into Cancelled """
        self.write({'state': 'cancel'})
        return True

    @api.one
    def action_cancel_draft(self):
        """ Go from cancelled state to draf state """
        self.write({'state': 'draft'})
        return True

    @api.one
    def action_send(self):
        """ Put the state of the letter into sent """
        self.write({
            'state': 'sent',
            'snd_date': self.snd_date or fields.Date.today()
        })
        return True

    @api.one
    def action_received(self):
        """ Put the state of the letter into Received """
        self.write({
            'state': 'rec',
            'rec_date': self.rec_date or fields.Date.today()
        })
        return True

    @api.one
    def action_rec_ret(self):
        """ Put the state of the letter into Received but Returned """
        self.write({
            'state': 'rec_ret',
            'rec_date': self.rec_date or fields.Date.today()
        })
        return True

    @api.one
    def action_rec_bad(self):
        """ Put the state of the letter into Received but Damaged """
        self.write({
            'state': 'rec_bad',
            'rec_date': self.rec_date or fields.Date.today()
        })
        return True
