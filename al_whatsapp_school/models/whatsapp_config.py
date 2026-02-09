from odoo import api, fields, models


class WhatsAppConfig(models.Model):
    _name = 'whatsapp.config'
    _description = 'Konfigurasi WhatsApp API'
    _rec_name = 'provider'

    provider = fields.Selection([
        ('waha', 'WAHA (Self-Hosted)'),
        ('fonnte', 'Fonnte'),
        ('wablas', 'WaBlas'),
        ('woowa', 'Woowa'),
        ('custom', 'Custom API'),
    ], string='Provider', required=True, default='waha')

    api_url = fields.Char(
        string='API URL',
        help='URL endpoint untuk mengirim pesan WhatsApp'
    )
    api_token = fields.Char(
        string='API Token',
        help='Token autentikasi untuk API WhatsApp (kosongkan jika WAHA tanpa auth)'
    )
    waha_session = fields.Char(
        string='WAHA Session',
        default='default',
        help='Nama session WAHA (default: default)'
    )
    sender_number = fields.Char(
        string='Nomor Pengirim',
        help='Nomor WhatsApp yang terdaftar sebagai pengirim'
    )

    is_active = fields.Boolean(string='Aktif', default=True)

    message_template = fields.Text(
        string='Template Pesan',
        default="""Assalamu'alaikum Bapak/Ibu,

Kami informasikan bahwa putra/putri Bapak/Ibu:

Nama: {nama_siswa}
Kelas: {kelas}
NIS: {nis}

Tidak hadir (Alfa) pada tanggal {tanggal} untuk mata pelajaran {mapel}.

Mohon konfirmasi dan koordinasi lebih lanjut dengan pihak sekolah.

Terima kasih.
Wassalamu'alaikum""",
        help='Template pesan WhatsApp. Variabel: {nama_siswa}, {kelas}, {nis}, {tanggal}, {mapel}'
    )

    send_to_ayah = fields.Boolean(string='Kirim ke Ayah', default=True)
    send_to_ibu = fields.Boolean(string='Kirim ke Ibu', default=True)
    send_to_wali = fields.Boolean(string='Kirim ke Wali', default=True)

    @api.model
    def get_active_config(self):
        return self.search([('is_active', '=', True)], limit=1)

    @api.onchange('provider')
    def _onchange_provider(self):
        if self.provider == 'waha':
            self.api_url = 'http://localhost:3000/api/sendText'
        elif self.provider == 'fonnte':
            self.api_url = 'https://api.fonnte.com/send'
        elif self.provider == 'wablas':
            self.api_url = 'https://pati.wablas.com/api/send-message'
        elif self.provider == 'woowa':
            self.api_url = 'https://api.woowa.id/send-message'
        else:
            self.api_url = ''
