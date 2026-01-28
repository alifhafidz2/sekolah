from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Nilai(models.Model):
    _name = 'sekolah.nilai'
    _description = 'Nilai Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tahun_ajaran_id desc, semester desc, siswa_id'

    siswa_id = fields.Many2one('sekolah.siswa', string='Siswa', required=True, tracking=True)
    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas', related='siswa_id.kelas_id', store=True)
    mata_pelajaran_id = fields.Many2one('sekolah.mata_pelajaran', string='Mata Pelajaran',
                                         required=True, tracking=True)
    guru_id = fields.Many2one('sekolah.guru', string='Guru Pengajar', tracking=True)

    tahun_ajaran_id = fields.Many2one('sekolah.tahun_ajaran', string='Tahun Ajaran', required=True)
    semester = fields.Selection(related='tahun_ajaran_id.semester', string='Semester', store=True)

    nilai_tugas = fields.Float(string='Nilai Tugas', digits=(5, 2), default=0.0)
    nilai_uts = fields.Float(string='Nilai UTS', digits=(5, 2), default=0.0)
    nilai_uas = fields.Float(string='Nilai UAS', digits=(5, 2), default=0.0)
    nilai_praktik = fields.Float(string='Nilai Praktik', digits=(5, 2), default=0.0)

    bobot_tugas = fields.Float(string='Bobot Tugas (%)', default=20.0)
    bobot_uts = fields.Float(string='Bobot UTS (%)', default=25.0)
    bobot_uas = fields.Float(string='Bobot UAS (%)', default=35.0)
    bobot_praktik = fields.Float(string='Bobot Praktik (%)', default=20.0)

    nilai_akhir = fields.Float(string='Nilai Akhir', compute='_compute_nilai_akhir',
                                store=True, digits=(5, 2))

    kkm = fields.Float(string='KKM', related='mata_pelajaran_id.kkm', store=True)

    status_kelulusan = fields.Selection([
        ('lulus', 'Lulus'),
        ('tidak_lulus', 'Tidak Lulus'),
        ('remedial', 'Remedial')
    ], string='Status Kelulusan', compute='_compute_status_kelulusan', store=True)

    predikat = fields.Selection([
        ('a', 'A (90-100)'),
        ('b', 'B (80-89)'),
        ('c', 'C (70-79)'),
        ('d', 'D (60-69)'),
        ('e', 'E (0-59)')
    ], string='Predikat', compute='_compute_predikat', store=True)

    catatan = fields.Text(string='Catatan Guru')

    @api.depends('nilai_tugas', 'nilai_uts', 'nilai_uas', 'nilai_praktik',
                 'bobot_tugas', 'bobot_uts', 'bobot_uas', 'bobot_praktik')
    def _compute_nilai_akhir(self):
        for record in self:
            record.nilai_akhir = (
                (record.nilai_tugas * record.bobot_tugas / 100) +
                (record.nilai_uts * record.bobot_uts / 100) +
                (record.nilai_uas * record.bobot_uas / 100) +
                (record.nilai_praktik * record.bobot_praktik / 100)
            )

    @api.depends('nilai_akhir', 'kkm')
    def _compute_status_kelulusan(self):
        for record in self:
            if record.nilai_akhir >= record.kkm:
                record.status_kelulusan = 'lulus'
            elif record.nilai_akhir >= (record.kkm - 10):
                record.status_kelulusan = 'remedial'
            else:
                record.status_kelulusan = 'tidak_lulus'

    @api.depends('nilai_akhir')
    def _compute_predikat(self):
        for record in self:
            if record.nilai_akhir >= 90:
                record.predikat = 'a'
            elif record.nilai_akhir >= 80:
                record.predikat = 'b'
            elif record.nilai_akhir >= 70:
                record.predikat = 'c'
            elif record.nilai_akhir >= 60:
                record.predikat = 'd'
            else:
                record.predikat = 'e'

    @api.constrains('nilai_tugas', 'nilai_uts', 'nilai_uas', 'nilai_praktik')
    def _check_nilai_range(self):
        for record in self:
            for field_name in ['nilai_tugas', 'nilai_uts', 'nilai_uas', 'nilai_praktik']:
                nilai = getattr(record, field_name)
                if nilai < 0 or nilai > 100:
                    raise ValidationError(f'{field_name.replace("_", " ").title()} harus antara 0-100!')

    @api.constrains('bobot_tugas', 'bobot_uts', 'bobot_uas', 'bobot_praktik')
    def _check_bobot_total(self):
        for record in self:
            total = record.bobot_tugas + record.bobot_uts + record.bobot_uas + record.bobot_praktik
            if abs(total - 100) > 0.01:
                raise ValidationError('Total bobot harus 100%!')

    @api.constrains('siswa_id', 'mata_pelajaran_id', 'tahun_ajaran_id', 'semester')
    def _check_duplicate(self):
        for record in self:
            duplicate = self.search([
                ('id', '!=', record.id),
                ('siswa_id', '=', record.siswa_id.id),
                ('mata_pelajaran_id', '=', record.mata_pelajaran_id.id),
                ('tahun_ajaran_id', '=', record.tahun_ajaran_id.id),
                ('semester', '=', record.semester)
            ])
            if duplicate:
                raise ValidationError(
                    f'Nilai untuk siswa {record.siswa_id.name} pada mata pelajaran '
                    f'{record.mata_pelajaran_id.name} semester ini sudah ada!'
                )
