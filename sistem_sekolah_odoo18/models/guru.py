from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Guru(models.Model):
    _name = 'sekolah.guru'
    _description = 'Data Guru'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'nip asc'

    name = fields.Char(string='Nama Lengkap', required=True, tracking=True)
    nip = fields.Char(string='NIP', required=True, copy=False, tracking=True)
    nuptk = fields.Char(string='NUPTK', copy=False)

    jenis_kelamin = fields.Selection([
        ('laki', 'Laki-laki'),
        ('perempuan', 'Perempuan')
    ], string='Jenis Kelamin', required=True, tracking=True)

    tempat_lahir = fields.Char(string='Tempat Lahir')
    tanggal_lahir = fields.Date(string='Tanggal Lahir', tracking=True)

    alamat = fields.Text(string='Alamat')
    telepon = fields.Char(string='Telepon')
    email = fields.Char(string='Email')

    spesialisasi = fields.Char(string='Spesialisasi/Bidang Keahlian')
    pendidikan_terakhir = fields.Selection([
        ('d3', 'D3'),
        ('s1', 'S1'),
        ('s2', 'S2'),
        ('s3', 'S3')
    ], string='Pendidikan Terakhir', default='s1')

    institusi_pendidikan = fields.Char(string='Institusi Pendidikan')
    jurusan = fields.Char(string='Jurusan')

    status_kepegawaian = fields.Selection([
        ('pns', 'PNS'),
        ('honorer', 'Honorer'),
        ('kontrak', 'Kontrak')
    ], string='Status Kepegawaian', default='honorer', tracking=True)

    tanggal_bergabung = fields.Date(string='Tanggal Bergabung', default=fields.Date.today)

    foto = fields.Image(string='Foto', max_width=200, max_height=200)

    mata_pelajaran_ids = fields.Many2many(
        'sekolah.mata_pelajaran',
        'guru_mapel_rel',
        'guru_id',
        'mapel_id',
        string='Mata Pelajaran yang Diampu'
    )

    jadwal_ids = fields.One2many('sekolah.jadwal', 'guru_id', string='Jadwal Mengajar')
    wali_kelas_ids = fields.One2many('sekolah.kelas', 'wali_kelas_id', string='Wali Kelas')

    is_wali_kelas = fields.Boolean(string='Adalah Wali Kelas', compute='_compute_is_wali_kelas', store=True)

    status = fields.Selection([
        ('aktif', 'Aktif'),
        ('cuti', 'Cuti'),
        ('pensiun', 'Pensiun'),
        ('resign', 'Resign')
    ], string='Status', default='aktif', required=True, tracking=True)

    user_id = fields.Many2one('res.users', string='Portal User', domain=[('share', '=', True)])

    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('nip_unique', 'unique(nip)', 'NIP harus unik!')
    ]

    @api.depends('wali_kelas_ids')
    def _compute_is_wali_kelas(self):
        for record in self:
            record.is_wali_kelas = bool(record.wali_kelas_ids)

    def action_view_jadwal(self):
        self.ensure_one()
        return {
            'name': f'Jadwal Mengajar - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sekolah.jadwal',
            'view_mode': 'calendar,list,form',
            'domain': [('guru_id', '=', self.id)],
            'context': {'default_guru_id': self.id}
        }

    def action_view_kelas_wali(self):
        self.ensure_one()
        return {
            'name': f'Kelas yang Diwalikan - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'sekolah.kelas',
            'view_mode': 'kanban,list,form',
            'domain': [('wali_kelas_id', '=', self.id)],
        }
