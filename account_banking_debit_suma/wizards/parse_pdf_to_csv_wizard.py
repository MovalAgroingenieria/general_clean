# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import base64
import csv
from io import BytesIO
import cStringIO
import PyPDF2


class PdfToCsvWizard(models.TransientModel):
    _name = 'pdf.to.csv.wizard'
    _description = 'Wizard to convert PDF to CSV'

    pdf_file = fields.Binary(
        string='PDF File',
        required=True)

    pdf_filename = fields.Char(
        string='Filename')

    file_type = fields.Selection([
        ('cancelations_generation_lid', 'Cancelations generation lid'),
        ('cancellations_in_voluntary', 'Cancellations in voluntary'),
        ('split_receipts', 'Split receipts')],
        string='File type',
        required=True
        )

    csv_file = fields.Binary(
        string='CSV File',
        readonly=True)

    csv_filename = fields.Char(
        string='CSV Filename',
        readonly=True)

    @api.multi
    def parse_pdf_to_csv(self):
        self.ensure_one()
        if not self.pdf_file:
            return

        pdf_stream = BytesIO(base64.b64decode(self.pdf_file))
        reader = PyPDF2.PdfFileReader(pdf_stream)

        if self.file_type == 'cancelations_generation_lid':
            csv_content = self._parse_cancelations_generation_lid(reader)
        elif self.file_type == 'cancellations_in_voluntary':
            csv_content = self._parse_cancellations_in_voluntary(reader)
        elif self.file_type == 'split_receipts':
            csv_content = self._parse_split_receipts(reader)
        else:
            csv_content = ''

        self.csv_file = base64.b64encode(csv_content)
        self.csv_filename = self.pdf_filename.replace(
            '.pdf', '.csv') if self.pdf_filename else 'output.csv'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'pdf.to.csv.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _parse_cancelations_generation_lid(self, reader):
        output = cStringIO.StringIO()
        writer = csv.writer(output)
        for page_num in range(reader.numPages):
            text = reader.getPage(page_num).extractText()
            # Parse doc
            lines = text.split('\n')
            # Write CSV
            for line in lines:
                writer.writerow([line.encode('utf-8')])
        return output.getvalue()

    def _parse_cancellations_in_voluntary(self, reader):
        output = cStringIO.StringIO()
        writer = csv.writer(output)
        for page_num in range(reader.numPages):
            text = reader.getPage(page_num).extractText()
            # Parse doc
            lines = text.split('\n')
            # Write CSV
            for line in lines:
                writer.writerow([line.encode('utf-8')])
        return output.getvalue()

    def _parse_split_receipts(self, reader):
        output = cStringIO.StringIO()
        writer = csv.writer(output)
        for page_num in range(reader.numPages):
            text = reader.getPage(page_num).extractText()
            # Parse doc
            lines = text.split('\n')
            # Write CSV
            for line in lines:
                writer.writerow([line.encode('utf-8')])
        return output.getvalue()
