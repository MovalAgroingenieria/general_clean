# -*- coding: utf-8 -*-
# 2021 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class SimpleattachmentModel(models.AbstractModel):
    _name = 'simpleattachment.model'
    _description = 'Simple-Attachment Model'

    number_of_attachments = fields.Integer(
        string='Number of attachments',
        compute='_compute_number_of_attachments')

    has_attachments = fields.Boolean(
        string='Has attachments',
        compute='_compute_has_attachments',
        search='_search_has_attachments')

    @api.multi
    def _compute_number_of_attachments(self):
        ir_attachment_model = self.env['ir.attachment'].sudo()
        for record in self:
            number_of_attachments = 0
            res_model = self.__class__._name
            res_id = record.id
            attachments = ir_attachment_model.search(
                [('res_model', '=', res_model),
                 ('res_id', '=', res_id)])
            if attachments:
                number_of_attachments = len(attachments)
            record.number_of_attachments = number_of_attachments

    @api.multi
    def _compute_has_attachments(self):
        for record in self:
            has_attachments = False
            if record.number_of_attachments > 0:
                has_attachments = True
            record.has_attachments = has_attachments

    def _search_has_attachments(self, operator, value):
        with_attachments = ((operator == '=' and value) or
                            (operator == '!=' and not value))
        ids = self.get_ids_of_model_with_attachments(
            self.__class__._name, with_attachments)
        return ([('id', '=', ids)])

    def get_ids_of_model_with_attachments(self,
                                          model_name, with_attachments=True):
        resp = []
        if model_name:
            table_name = model_name.replace('.', '_')
            sql_with_attachments = \
                'SELECT DISTINCT res_id FROM ir_attachment ' + \
                'WHERE res_model = \'' + model_name + '\' ' + \
                'AND res_id IS NOT NULL'
            sql_without_attachments = \
                'SELECT id FROM ' + table_name + ' ' + \
                'WHERE id NOT IN (' + sql_with_attachments + ')'
            sql = sql_with_attachments
            if (not with_attachments):
                sql = sql_without_attachments
            self.env.cr.execute(sql)
            sql_resp = self.env.cr.fetchall()
            if sql_resp:
                for item in sql_resp:
                    resp.append(item[0])
        return resp
