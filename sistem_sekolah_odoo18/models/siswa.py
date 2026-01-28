from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Siswa(models.Model):
    _name = 'sekolah.siswa'
    _description = 'Data Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nis asc'

    name = fields.Char(string='Nama Lengkap', required=True, tracking=True)
    nis = fields.Char(string='NIS', required=True, copy=False, tracking=True)
    nisn = fields.Char(string='NISN', copy=False)
    jenis_kelamin = fields.Selection([
        ('laki', 'Laki-laki'),
        ('perempuan', 'Perempuan')
    ], string='Jenis Kelamin', required=True, tracking=True)

    tempat_lahir = fields.Char(string='Tempat Lahir')
    tanggal_lahir = fields.Date(string='Tanggal Lahir', tracking=True)
    umur = fields.Integer(string='Umur', compute='_compute_umur', store=True)

    alamat = fields.Text(string='Alamat')
    rt = fields.Char(string='RT')
    rw = fields.Char(string='RW')
    kelurahan = fields.Char(string='Kelurahan')
    kecamatan = fields.Char(string='Kecamatan')
    kota = fields.Char(string='Kota/Kabupaten')
    provinsi = fields.Char(string='Provinsi')
    kode_pos = fields.Char(string='Kode Pos')

    telepon = fields.Char(string='Telepon')
    email = fields.Char(string='Email')

    nama_ayah = fields.Char(string='Nama Ayah')
    pekerjaan_ayah = fields.Char(string='Pekerjaan Ayah')
    telepon_ayah = fields.Char(string='Telepon Ayah')

    nama_ibu = fields.Char(string='Nama Ibu')
    pekerjaan_ibu = fields.Char(string='Pekerjaan Ibu')
    telepon_ibu = fields.Char(string='Telepon Ibu')

    nama_wali = fields.Char(string='Nama Wali')
    hubungan_wali = fields.Char(string='Hubungan dengan Wali')
    telepon_wali = fields.Char(string='Telepon Wali')

    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas', tracking=True)
    tingkat = fields.Selection(related='kelas_id.tingkat', string='Tingkat', store=True)

    tanggal_masuk = fields.Date(string='Tanggal Masuk', default=fields.Date.today, tracking=True)
    status = fields.Selection([
        ('aktif', 'Aktif'),
        ('lulus', 'Lulus'),
        ('pindah', 'Pindah'),
        ('keluar', 'Keluar'),
        ('cuti', 'Cuti')
    ], string='Status', default='aktif', required=True, tracking=True)

    foto = fields.Image(string='Foto', max_width=200, max_height=200)

    absensi_ids = fields.One2many('sekolah.absensi', 'siswa_id', string='Riwayat Absensi')
    nilai_ids = fields.One2many('sekolah.nilai', 'siswa_id', string='Daftar Nilai')

    total_absensi = fields.Integer(string='Total Absensi', compute='_compute_statistik_absensi')
    total_hadir = fields.Integer(string='Total Hadir', compute='_compute_statistik_absensi')
    total_izin = fields.Integer(string='Total Izin', compute='_compute_statistik_absensi')
    total_sakit = fields.Integer(string='Total Sakit', compute='_compute_statistik_absensi')
    total_alfa = fields.Integer(string='Total Alfa', compute='_compute_statistik_absensi')
    persentase_kehadiran = fields.Float(string='Persentase Kehadiran (%)', compute='_compute_statistik_absensi')

    rata_rata_nilai = fields.Float(string='Rata-rata Nilai', compute='_compute_rata_nilai', digits=(5, 2))

    user_id = fields.Many2one('res.users', string='Portal User', domain=[('share', '=', True)])

    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('nis_unique', 'unique(nis)', 'NIS harus unik!'),
        ('nisn_unique', 'unique(nisn)', 'NISN harus unik!')
    ]

    @api.depends('tanggal_lahir')
    def _compute_umur(self):
        for record in self:
            if record.tanggal_lahir:
                today = fields.Date.today()
                delta = relativedelta(today, record.tanggal_lahir)
                record.umur = delta.years
            else:
                record.umur = 0

    @api.depends('absensi_ids', 'absensi_ids.status')
    def _compute_statistik_absensi(self):
        for record in self:
            absensi = record.absensi_ids
            record.total_absensi = len(absensi)
            record.total_hadir = len(absensi.filtered(lambda a: a.status == 'hadir'))
            record.total_izin = len(absensi.filtered(lambda a: a.status == 'izin'))
            record.total_sakit = len(absensi.filtered(lambda a: a.status == 'sakit'))
            record.total_alfa = len(absensi.filtered(lambda a: a.status == 'alfa'))

            if record.total_absensi > 0:
                record.persentase_kehadiran = (record.total_hadir / record.total_absensi) * 100
            else:
                record.persentase_kehadiran = 0.0

    @api.depends('nilai_ids', 'nilai_ids.nilai_akhir')
    def _compute_rata_nilai(self):
        for record in self:
            nilai_list = record.nilai_ids.filtered(lambda n: n.nilai_akhir > 0)
            if nilai_list:
                record.rata_rata_nilai = sum(nilai_list.mapped('nilai_akhir')) / len(nilai_list)
            else:
                record.rata_rata_nilai = 0.0

    @api.onchange('status')
    def _onchange_status(self):
        if self.status in ['lulus', 'pindah', 'keluar']:
            self.kelas_id = False

    def action_view_absensi(self):
        self.ensure_one()
        return {
            'name': f'Absensi - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sekolah.absensi',
            'view_mode': 'tree,form',
            'domain': [('siswa_id', '=', self.id)],
            'context': {'default_siswa_id': self.id}
        }

    def action_view_nilai(self):
        self.ensure_one()
        return {
            'name': f'Nilai - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sekolah.nilai',
            'view_mode': 'tree,form',
            'domain': [('siswa_id', '=', self.id)],
            'context': {'default_siswa_id': self.id}
        }
