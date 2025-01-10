# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo import models, fields, api


class ResLetter(models.Model):
    _inherit = 'res.letter'

    # electronicfile_communication_id = fields.Many2one(
    #     string='Communication',
    #     comodel_name='eom.electronicfile.communication',
    #     ondelete='restrict',
    #     track_visibility='onchange')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
    #                     submenu=False):
    #     res = super(ResLetter, self).fields_view_get(
    #         view_id=view_id, view_type=view_type, toolbar=toolbar,
    #         submenu=submenu)
    #     access_file_filemgmt = \
    #         self.env['res.file']._check_access_file_filemgmt()
    #     if view_type == 'form':
    #         doc = etree.XML(res['arch'])
    #         if not access_file_filemgmt:
    #             for node in doc.xpath(
    #                     "//field[@name='electronicfile_communication_id']"):
    #                 node.set('modifiers', '{"invisible": true}')
    #         res['arch'] = etree.tostring(doc)
    #     if view_type == 'tree':
    #         doc = etree.XML(res['arch'])
    #         if not access_file_filemgmt:
    #             for node in doc.xpath(
    #                     "//field[@name='electronicfile_communication_id']"):
    #                 node.set('invisible', '1')
    #                 node.set('modifiers', '{"tree_invisible": true}')
    #         res['arch'] = etree.tostring(doc)
    #     if view_type == 'search':
    #         doc = etree.XML(res['arch'])
    #         if not access_file_filemgmt:
    #             for node in doc.xpath(
    #                     "//field[@name='electronicfile_communication_id']"):
    #                 node.set('invisible', '1')
    #                 node.set('modifiers', '{"invisible": true}')
    #         res['arch'] = etree.tostring(doc)
    #     return res
