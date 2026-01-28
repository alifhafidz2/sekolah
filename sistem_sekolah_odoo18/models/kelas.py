from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Kelas(models.Model):
    _name = 'sekolah.kelas'
    _description = 'Data Kelas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tingkat asc, name asc'

    name = fields.Char(string='Nama Kelas', required=True, tracking=True)
    tingkat = fields.Selection([
        ('10', 'Kelas 10'),
        ('11', 'Kelas 11'),
        ('12', 'Kelas 12')
    ], string='Tingkat', required=True, tracking=True)

    jurusan = fields.Selection([
        ('ipa', 'IPA'),
        ('ips', 'IPS'),
        ('bahasa', 'Bahasa'),
        ('umum', 'Umum')
    ], string='Jurusan', default='umum')

    wali_kelas_id = fields.Many2one('sekolah.guru', string='Wali Kelas', tracking=True)
    tahun_ajaran_id = fields.Many2one('sekolah.tahun_ajaran', string='Tahun Ajaran')

    kapasitas = fields.Integer(string='Kapasitas', default=30, tracking=True)

    siswa_ids = fields.One2many('sekolah.siswa', 'kelas_id', string='Daftar Siswa')
    jumlah_siswa = fields.Integer(string='Jumlah Siswa', compute='_compute_jumlah_siswa', store=True)

    jadwal_ids = fields.One2many('sekolah.jadwal', 'kelas_id', string='Jadwal Pelajaran')

    is_full = fields.Boolean(string='Kelas Penuh', compute='_compute_is_full', store=True)
    persentase_terisi = fields.Float(string='Persentase Terisi (%)', compute='_compute_persentase', store=True)

    ruang_kelas = fields.Char(string='Ruang Kelas')

    keterangan = fields.Text(string='Keterangan')

    active = fields.Boolean(string='Active', default=True)

    @api.depends('siswa_ids')
    def _compute_jumlah_siswa(self):
        for record in self:
            record.jumlah_siswa = len(record.siswa_ids.filtered(lambda s: s.status == 'aktif'))

    @api.depends('jumlah_siswa', 'kapasitas')
    def _compute_is_full(self):
        for record in self:
            record.is_full = record.jumlah_siswa >= record.kapasitas

    @api.depends('jumlah_siswa', 'kapasitas')
    def _compute_persentase(self):
        for record in self:
            if record.kapasitas > 0:
                record.persentase_terisi = (record.jumlah_siswa / record.kapasitas) * 100
            else:
                record.persentase_terisi = 0.0

    @api.constrains('jumlah_siswa', 'kapasitas')
    def _check_kapasitas(self):
        for record in self:
            if record.jumlah_siswa > record.kapasitas:
                raise ValidationError(f'Jumlah siswa melebihi kapasitas kelas! (Max: {record.kapasitas})')

    def action_view_siswa(self):
        self.ensure_one()
        return {
            'name': f'Siswa - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sekolah.siswa',
            'view_mode': 'kanban,tree,form',
            'domain': [('kelas_id', '=', self.id)],
            'context': {'default_kelas_id': self.id}
        }

    def action_view_jadwal(self):
        self.ensure_one()
        return {
            'name': f'Jadwal - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sekolah.jadwal',
            'view_mode': 'calendar,tree,form',
            'domain': [('kelas_id', '=', self.id)],
            'context': {'default_kelas_id': self.id}
        }
