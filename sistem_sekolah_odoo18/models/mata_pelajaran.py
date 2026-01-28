from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MataPelajaran(models.Model):
    _name = 'sekolah.mata_pelajaran'
    _description = 'Mata Pelajaran'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'kode asc'

    name = fields.Char(string='Nama Mata Pelajaran', required=True, tracking=True)
    kode = fields.Char(string='Kode', required=True, copy=False, tracking=True)

    kategori = fields.Selection([
        ('wajib', 'Mata Pelajaran Wajib'),
        ('peminatan', 'Mata Pelajaran Peminatan'),
        ('lintas_minat', 'Mata Pelajaran Lintas Minat'),
        ('pendalaman', 'Pendalaman Minat')
    ], string='Kategori', default='wajib', required=True)

    kelompok = fields.Selection([
        ('a', 'Kelompok A (Umum)'),
        ('b', 'Kelompok B (Umum)'),
        ('c', 'Kelompok C (Peminatan)')
    ], string='Kelompok Mata Pelajaran', default='a')

    sks = fields.Integer(string='SKS/Jam Pelajaran per Minggu', default=2)
    kkm = fields.Float(string='KKM (Kriteria Ketuntasan Minimal)', default=75.0, digits=(5, 2))

    deskripsi = fields.Text(string='Deskripsi')

    guru_ids = fields.Many2many(
        'sekolah.guru',
        'guru_mapel_rel',
        'mapel_id',
        'guru_id',
        string='Guru Pengampu'
    )

    jadwal_ids = fields.One2many('sekolah.jadwal', 'mata_pelajaran_id', string='Jadwal')
    nilai_ids = fields.One2many('sekolah.nilai', 'mata_pelajaran_id', string='Nilai')

    jumlah_guru = fields.Integer(string='Jumlah Guru', compute='_compute_jumlah_guru')

    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('kode_unique', 'unique(kode)', 'Kode mata pelajaran harus unik!')
    ]

    @api.depends('guru_ids')
    def _compute_jumlah_guru(self):
        for record in self:
            record.jumlah_guru = len(record.guru_ids)

    @api.constrains('kkm')
    def _check_kkm(self):
        for record in self:
            if record.kkm < 0 or record.kkm > 100:
                raise ValidationError('KKM harus antara 0 sampai 100!')

    @api.constrains('sks')
    def _check_sks(self):
        for record in self:
            if record.sks <= 0:
                raise ValidationError('SKS/Jam pelajaran harus lebih dari 0!')
