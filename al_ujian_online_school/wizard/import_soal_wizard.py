from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import csv
import io


class ImportSoalWizard(models.TransientModel):
    _name = 'ujian.import_soal_wizard'
    _description = 'Import Soal dari CSV'

    kategori_id = fields.Many2one(
        'ujian.kategori_soal',
        string='Kategori',
        required=True
    )
    file = fields.Binary(string='File CSV', required=True)
    filename = fields.Char(string='Nama File')
    delimiter = fields.Selection([
        (',', 'Koma (,)'),
        (';', 'Titik Koma (;)'),
        ('\t', 'Tab'),
    ], string='Delimiter', default=',', required=True)
    preview = fields.Text(string='Preview', readonly=True)

    @api.onchange('file', 'delimiter')
    def _onchange_file(self):
        if self.file:
            try:
                content = base64.b64decode(self.file).decode('utf-8')
                reader = csv.reader(io.StringIO(content), delimiter=self.delimiter)
                rows = list(reader)[:6]
                preview_lines = []
                for i, row in enumerate(rows):
                    if i == 0:
                        preview_lines.append("Header: " + " | ".join(row))
                    else:
                        preview_lines.append(f"Baris {i}: " + " | ".join(row[:3]) + "...")
                self.preview = "\n".join(preview_lines)
            except Exception as e:
                self.preview = f"Error: {str(e)}"

    def action_import(self):
        self.ensure_one()
        if not self.file:
            raise UserError('Silakan pilih file CSV!')
        try:
            content = base64.b64decode(self.file).decode('utf-8')
            reader = csv.DictReader(io.StringIO(content), delimiter=self.delimiter)
            soal_vals = []
            for row in reader:
                tipe_soal = row.get('tipe_soal', 'pg').lower()
                tingkat = row.get('tingkat_kesulitan', 'sedang').lower()
                vals = {
                    'kategori_id': self.kategori_id.id,
                    'tipe_soal': tipe_soal,
                    'tingkat_kesulitan': tingkat,
                    'pertanyaan': row.get('pertanyaan', ''),
                    'bobot': float(row.get('bobot', 1)),
                    'pembahasan': row.get('pembahasan', ''),
                }
                if tipe_soal in ['pg', 'benar_salah']:
                    pilihan_a = row.get('pilihan_a', '')
                    pilihan_b = row.get('pilihan_b', '')
                    pilihan_c = row.get('pilihan_c', '')
                    pilihan_d = row.get('pilihan_d', '')
                    pilihan_e = row.get('pilihan_e', '')
                    jawaban_benar = row.get('jawaban_benar', 'A').upper()
                    pilihan_vals = []
                    for i, (label, teks) in enumerate([('A', pilihan_a), ('B', pilihan_b), ('C', pilihan_c), ('D', pilihan_d), ('E', pilihan_e)]):
                        if teks:
                            pilihan_vals.append((0, 0, {
                                'sequence': (i + 1) * 10,
                                'teks': teks,
                                'is_correct': label == jawaban_benar,
                            }))
                    vals['pilihan_ids'] = pilihan_vals
                elif tipe_soal == 'isian':
                    vals['jawaban_benar'] = row.get('jawaban_benar', '')
                    vals['jawaban_benar_alt'] = row.get('jawaban_alternatif', '')
                soal_vals.append(vals)
            created = self.env['ujian.bank_soal'].create(soal_vals)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Berhasil',
                    'message': f'{len(created)} soal berhasil diimport',
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window',
                        'res_model': 'ujian.bank_soal',
                        'view_mode': 'list,form',
                        'domain': [('id', 'in', created.ids)],
                    }
                }
            }
        except Exception as e:
            raise UserError(f'Error saat import: {str(e)}')
