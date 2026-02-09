from odoo import api, fields, models


class WhatsAppLog(models.Model):
    _name = 'whatsapp.log'
    _description = 'Log Pengiriman WhatsApp'
    _order = 'create_date desc'

    siswa_id = fields.Many2one('sekolah.siswa', string='Siswa', required=True)
    absensi_id = fields.Many2one('sekolah.absensi', string='Absensi')
    phone_number = fields.Char(string='Nomor Telepon', required=True)
    recipient_type = fields.Selection([
        ('ayah', 'Ayah'),
        ('ibu', 'Ibu'),
        ('wali', 'Wali'),
    ], string='Penerima')
    message = fields.Text(string='Pesan')
    status = fields.Selection([
        ('pending', 'Menunggu'),
        ('sent', 'Terkirim'),
        ('failed', 'Gagal'),
    ], string='Status', default='pending')
    response = fields.Text(string='Response API')
    error_message = fields.Text(string='Pesan Error')
    sent_date = fields.Datetime(string='Tanggal Kirim')

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.siswa_id.name} - {rec.phone_number} ({rec.status})"
            result.append((rec.id, name))
        return result
