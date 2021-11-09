# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class Binary(http.Controller):

    @http.route('/web/binary/download_sms_attachment/<int:id>', type='http',
                auth='user')
    def download_sms_attachment(self, id):
        attachment = request.env['ir.attachment'].browse(id)
        pdfhttpheaders = [('Content-Type', 'application/pdf')]
        file_decoded = attachment.datas.decode('base64')
        return request.make_response(file_decoded, headers=pdfhttpheaders)
