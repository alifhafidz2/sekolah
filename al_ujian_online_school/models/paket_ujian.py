from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import random


class PaketUjian(models.Model):
    _name = 'ujian.paket'
    _description = 'Paket Ujian'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tanggal_mulai desc, id desc'

    name = fields.Char(
        string='Kode Ujian',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    judul = fields.Char(string='Judul Ujian', required=True, tracking=True)
    jenis_ujian = fields.Selection([
        ('uh', 'Ulangan Harian'),
        ('pts', 'Penilaian Tengah Semester'),
        ('pas', 'Penilaian Akhir Semester'),
        ('pat', 'Penilaian Akhir Tahun'),
        ('try_out', 'Try Out'),
        ('remedial', 'Remedial'),
        ('pengayaan', 'Pengayaan'),
    ], string='Jenis Ujian', required=True, default='uh', tracking=True)
    mata_pelajaran_id = fields.Many2one(
        'sekolah.mata_pelajaran',
        string='Mata Pelajaran',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    tahun_ajaran_id = fields.Many2one(
        'sekolah.tahun_ajaran',
        string='Tahun Ajaran',
        required=True,
        ondelete='restrict'
    )
    guru_id = fields.Many2one(
        'sekolah.guru',
        string='Guru Pengampu',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    kelas_ids = fields.Many2many(
        'sekolah.kelas',
        'ujian_paket_kelas_rel',
        'paket_id',
        'kelas_id',
        string='Kelas Peserta',
        required=True
    )
    tanggal_mulai = fields.Datetime(
        string='Waktu Mulai',
        required=True,
        tracking=True
    )
    tanggal_selesai = fields.Datetime(
        string='Waktu Selesai',
        required=True,
        tracking=True
    )
    durasi = fields.Integer(
        string='Durasi (Menit)',
        required=True,
        default=60,
        tracking=True
    )
    soal_line_ids = fields.One2many(
        'ujian.paket_soal_line',
        'paket_id',
        string='Daftar Soal'
    )
    jumlah_soal = fields.Integer(
        string='Jumlah Soal',
        compute='_compute_jumlah_soal',
        store=True
    )
    total_bobot = fields.Float(
        string='Total Bobot',
        compute='_compute_jumlah_soal',
        store=True
    )
    passing_grade = fields.Float(
        string='KKM',
        default=75.0,
        required=True
    )
    acak_soal = fields.Boolean(
        string='Acak Urutan Soal',
        default=True,
        help='Urutan soal akan diacak untuk setiap siswa'
    )
    acak_jawaban = fields.Boolean(
        string='Acak Pilihan Jawaban',
        default=True,
        help='Urutan pilihan jawaban akan diacak'
    )
    tampilkan_hasil = fields.Boolean(
        string='Tampilkan Hasil',
        default=True,
        help='Siswa dapat melihat hasil setelah selesai ujian'
    )
    tampilkan_pembahasan = fields.Boolean(
        string='Tampilkan Pembahasan',
        default=False,
        help='Siswa dapat melihat pembahasan setelah selesai ujian'
    )
    satu_halaman = fields.Boolean(
        string='Semua Soal Satu Halaman',
        default=False,
        help='Tampilkan semua soal dalam satu halaman'
    )
    allow_back = fields.Boolean(
        string='Izinkan Kembali',
        default=True,
        help='Siswa dapat kembali ke soal sebelumnya'
    )
    max_attempt = fields.Integer(
        string='Maksimal Percobaan',
        default=1,
        help='Jumlah maksimal percobaan ujian (0 = tidak terbatas)'
    )
    petunjuk = fields.Html(
        string='Petunjuk Ujian',
        sanitize=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Siap'),
        ('active', 'Aktif'),
        ('done', 'Selesai'),
        ('cancel', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True)
    peserta_ids = fields.One2many(
        'ujian.peserta',
        'paket_id',
        string='Peserta Ujian'
    )
    peserta_count = fields.Integer(
        string='Jumlah Peserta',
        compute='_compute_peserta_stats'
    )
    peserta_selesai = fields.Integer(
        string='Sudah Selesai',
        compute='_compute_peserta_stats'
    )
    rata_rata = fields.Float(
        string='Rata-rata Nilai',
        compute='_compute_peserta_stats',
        digits=(5, 2)
    )
    nilai_tertinggi = fields.Float(
        string='Nilai Tertinggi',
        compute='_compute_peserta_stats',
        digits=(5, 2)
    )
    nilai_terendah = fields.Float(
        string='Nilai Terendah',
        compute='_compute_peserta_stats',
        digits=(5, 2)
    )
    lulus_count = fields.Integer(
        string='Lulus KKM',
        compute='_compute_peserta_stats'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ujian.paket') or 'New'
        return super().create(vals_list)

    @api.depends('soal_line_ids', 'soal_line_ids.bobot')
    def _compute_jumlah_soal(self):
        for rec in self:
            rec.jumlah_soal = len(rec.soal_line_ids)
            rec.total_bobot = sum(rec.soal_line_ids.mapped('bobot'))

    @api.depends('peserta_ids', 'peserta_ids.state', 'peserta_ids.nilai')
    def _compute_peserta_stats(self):
        for rec in self:
            peserta = rec.peserta_ids
            peserta_selesai = peserta.filtered(lambda p: p.state == 'selesai')
            rec.peserta_count = len(peserta)
            rec.peserta_selesai = len(peserta_selesai)
            if peserta_selesai:
                nilai_list = peserta_selesai.mapped('nilai')
                rec.rata_rata = sum(nilai_list) / len(nilai_list)
                rec.nilai_tertinggi = max(nilai_list)
                rec.nilai_terendah = min(nilai_list)
                rec.lulus_count = len(peserta_selesai.filtered(lambda p: p.nilai >= rec.passing_grade))
            else:
                rec.rata_rata = 0
                rec.nilai_tertinggi = 0
                rec.nilai_terendah = 0
                rec.lulus_count = 0

    @api.constrains('tanggal_mulai', 'tanggal_selesai')
    def _check_tanggal(self):
        for rec in self:
            if rec.tanggal_selesai <= rec.tanggal_mulai:
                raise ValidationError('Waktu selesai harus lebih besar dari waktu mulai!')

    @api.constrains('durasi')
    def _check_durasi(self):
        for rec in self:
            if rec.durasi <= 0:
                raise ValidationError('Durasi harus lebih dari 0 menit!')

    def action_set_ready(self):
        for rec in self:
            if not rec.soal_line_ids:
                raise UserError('Tidak ada soal dalam paket ujian ini!')
            rec.state = 'ready'

    def action_activate(self):
        for rec in self:
            if not rec.peserta_ids:
                raise UserError('Belum ada peserta ujian! Silakan generate peserta terlebih dahulu.')
            rec.state = 'active'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_generate_peserta(self):
        self.ensure_one()
        return {
            'name': 'Generate Peserta Ujian',
            'type': 'ir.actions.act_window',
            'res_model': 'ujian.generate_peserta_wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_paket_id': self.id}
        }

    def action_view_peserta(self):
        self.ensure_one()
        return {
            'name': 'Peserta Ujian',
            'type': 'ir.actions.act_window',
            'res_model': 'ujian.peserta',
            'view_mode': 'list,form',
            'domain': [('paket_id', '=', self.id)],
            'context': {'default_paket_id': self.id}
        }

    def action_view_hasil(self):
        self.ensure_one()
        return {
            'name': 'Hasil Ujian',
            'type': 'ir.actions.act_window',
            'res_model': 'ujian.peserta',
            'view_mode': 'list,pivot,graph',
            'domain': [('paket_id', '=', self.id), ('state', '=', 'selesai')],
            'context': {
                'search_default_group_by_kelas': 1,
            }
        }

    def get_shuffled_soal(self, peserta_id):
        self.ensure_one()
        soal_list = list(self.soal_line_ids.sorted('sequence'))
        if self.acak_soal:
            random.seed(peserta_id)
            random.shuffle(soal_list)
        return soal_list


class PaketSoalLine(models.Model):
    _name = 'ujian.paket_soal_line'
    _description = 'Soal dalam Paket Ujian'
    _order = 'sequence, id'

    paket_id = fields.Many2one(
        'ujian.paket',
        string='Paket Ujian',
        required=True,
        ondelete='cascade'
    )
    soal_id = fields.Many2one(
        'ujian.bank_soal',
        string='Soal',
        required=True,
        ondelete='restrict'
    )
    sequence = fields.Integer(string='Urutan', default=10)
    bobot = fields.Float(
        string='Bobot',
        related='soal_id.bobot',
        store=True
    )
    tipe_soal = fields.Selection(
        related='soal_id.tipe_soal',
        store=True,
        string='Tipe'
    )

    _sql_constraints = [
        ('paket_soal_unique', 'UNIQUE(paket_id, soal_id)', 'Soal sudah ada dalam paket ujian ini!')
    ]
