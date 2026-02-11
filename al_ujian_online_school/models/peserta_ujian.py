from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class PesertaUjian(models.Model):
    _name = 'ujian.peserta'
    _description = 'Peserta Ujian'
    _inherit = ['mail.thread']
    _order = 'paket_id, siswa_id'
    _rec_name = 'display_name'

    paket_id = fields.Many2one(
        'ujian.paket',
        string='Paket Ujian',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    siswa_id = fields.Many2one(
        'sekolah.siswa',
        string='Siswa',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    kelas_id = fields.Many2one(
        related='siswa_id.kelas_id',
        store=True,
        string='Kelas'
    )
    display_name = fields.Char(
        string='Nama',
        compute='_compute_display_name',
        store=True
    )
    state = fields.Selection([
        ('belum', 'Belum Mulai'),
        ('mengerjakan', 'Sedang Mengerjakan'),
        ('selesai', 'Selesai'),
    ], string='Status', default='belum', tracking=True)
    attempt = fields.Integer(string='Percobaan Ke', default=0)
    waktu_mulai = fields.Datetime(string='Waktu Mulai')
    waktu_selesai = fields.Datetime(string='Waktu Selesai')
    waktu_deadline = fields.Datetime(
        string='Batas Waktu',
        compute='_compute_waktu_deadline',
        store=True
    )
    durasi_aktual = fields.Integer(
        string='Durasi (Menit)',
        compute='_compute_durasi_aktual'
    )
    jawaban_ids = fields.One2many(
        'ujian.jawaban',
        'peserta_id',
        string='Jawaban'
    )
    jumlah_terjawab = fields.Integer(
        string='Terjawab',
        compute='_compute_nilai',
        store=True
    )
    jumlah_benar = fields.Integer(
        string='Benar',
        compute='_compute_nilai',
        store=True
    )
    jumlah_salah = fields.Integer(
        string='Salah',
        compute='_compute_nilai',
        store=True
    )
    nilai_mentah = fields.Float(
        string='Skor',
        compute='_compute_nilai',
        store=True,
        digits=(10, 2)
    )
    nilai = fields.Float(
        string='Nilai',
        compute='_compute_nilai',
        store=True,
        digits=(5, 2)
    )
    is_lulus = fields.Boolean(
        string='Lulus KKM',
        compute='_compute_nilai',
        store=True
    )
    token = fields.Char(string='Token Akses', copy=False)
    ip_address = fields.Char(string='IP Address')
    browser_info = fields.Char(string='Browser Info')
    current_soal = fields.Integer(string='Soal Saat Ini', default=0)
    soal_order = fields.Char(
        string='Urutan Soal',
        help='JSON array of soal IDs in shuffled order'
    )

    _sql_constraints = [
        ('peserta_unique', 'UNIQUE(paket_id, siswa_id)', 'Siswa sudah terdaftar dalam ujian ini!')
    ]

    @api.depends('siswa_id', 'paket_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.siswa_id and rec.paket_id:
                rec.display_name = f"{rec.siswa_id.name} - {rec.paket_id.judul}"
            else:
                rec.display_name = "New"

    @api.depends('waktu_mulai', 'paket_id.durasi')
    def _compute_waktu_deadline(self):
        for rec in self:
            if rec.waktu_mulai and rec.paket_id.durasi:
                rec.waktu_deadline = rec.waktu_mulai + timedelta(minutes=rec.paket_id.durasi)
            else:
                rec.waktu_deadline = False

    def _compute_durasi_aktual(self):
        for rec in self:
            if rec.waktu_mulai and rec.waktu_selesai:
                delta = rec.waktu_selesai - rec.waktu_mulai
                rec.durasi_aktual = int(delta.total_seconds() / 60)
            elif rec.waktu_mulai and rec.state == 'mengerjakan':
                delta = datetime.now() - rec.waktu_mulai
                rec.durasi_aktual = int(delta.total_seconds() / 60)
            else:
                rec.durasi_aktual = 0

    @api.depends('jawaban_ids', 'jawaban_ids.is_correct', 'jawaban_ids.poin_diperoleh', 'paket_id.total_bobot', 'paket_id.passing_grade')
    def _compute_nilai(self):
        for rec in self:
            jawaban = rec.jawaban_ids
            rec.jumlah_terjawab = len(jawaban.filtered(lambda j: j.jawaban or j.pilihan_id))
            rec.jumlah_benar = len(jawaban.filtered('is_correct'))
            rec.jumlah_salah = len(jawaban.filtered(lambda j: (j.jawaban or j.pilihan_id) and not j.is_correct))
            rec.nilai_mentah = sum(jawaban.mapped('poin_diperoleh'))
            if rec.paket_id.total_bobot > 0:
                rec.nilai = (rec.nilai_mentah / rec.paket_id.total_bobot) * 100
            else:
                rec.nilai = 0
            rec.is_lulus = rec.nilai >= rec.paket_id.passing_grade

    def action_start_ujian(self):
        self.ensure_one()
        now = datetime.now()
        if now < self.paket_id.tanggal_mulai:
            raise UserError('Ujian belum dimulai!')
        if now > self.paket_id.tanggal_selesai:
            raise UserError('Ujian sudah berakhir!')
        if self.paket_id.max_attempt > 0 and self.attempt >= self.paket_id.max_attempt:
            raise UserError('Anda sudah mencapai batas maksimal percobaan!')
        import secrets
        import json
        self.jawaban_ids.unlink()
        soal_lines = self.paket_id.get_shuffled_soal(self.id)
        soal_order = [line.soal_id.id for line in soal_lines]
        for line in soal_lines:
            self.env['ujian.jawaban'].create({
                'peserta_id': self.id,
                'soal_id': line.soal_id.id,
                'paket_line_id': line.id,
            })
        self.write({
            'state': 'mengerjakan',
            'waktu_mulai': now,
            'attempt': self.attempt + 1,
            'token': secrets.token_urlsafe(32),
            'current_soal': 0,
            'soal_order': json.dumps(soal_order),
        })
        return True

    def action_submit_ujian(self):
        self.ensure_one()
        now = datetime.now()
        for jawaban in self.jawaban_ids:
            jawaban._compute_correction()
        self.write({
            'state': 'selesai',
            'waktu_selesai': now,
        })
        return True

    def action_reset_ujian(self):
        self.ensure_one()
        self.jawaban_ids.unlink()
        self.write({
            'state': 'belum',
            'waktu_mulai': False,
            'waktu_selesai': False,
            'token': False,
            'current_soal': 0,
            'soal_order': False,
            'attempt': 0,
            'ip_address': False,
            'browser_info': False,
        })
        return True

    def action_view_jawaban(self):
        self.ensure_one()
        return {
            'name': f'Jawaban {self.siswa_id.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'ujian.jawaban',
            'view_mode': 'list,form',
            'domain': [('peserta_id', '=', self.id)],
        }

    def get_remaining_time(self):
        self.ensure_one()
        if not self.waktu_deadline:
            return 0
        now = datetime.now()
        if now >= self.waktu_deadline:
            return 0
        delta = self.waktu_deadline - now
        return int(delta.total_seconds())

    def check_auto_submit(self):
        peserta_timeout = self.search([
            ('state', '=', 'mengerjakan'),
            ('waktu_deadline', '<=', datetime.now())
        ])
        for peserta in peserta_timeout:
            peserta.action_submit_ujian()
        return True
