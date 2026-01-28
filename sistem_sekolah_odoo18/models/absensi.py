from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Absensi(models.Model):
    _name = 'sekolah.absensi'
    _description = 'Absensi Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tanggal desc, kelas_id, siswa_id'

    name = fields.Char(string='Kode Absensi', readonly=True, copy=False, default='New')

    tanggal = fields.Date(string='Tanggal', required=True, default=fields.Date.today, tracking=True)
    siswa_id = fields.Many2one('sekolah.siswa', string='Siswa', required=True, tracking=True)
    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas', related='siswa_id.kelas_id', store=True)

    jadwal_id = fields.Many2one('sekolah.jadwal', string='Jadwal/Mata Pelajaran')
    mata_pelajaran_id = fields.Many2one('sekolah.mata_pelajaran', string='Mata Pelajaran',
                                         related='jadwal_id.mata_pelajaran_id', store=True)
    guru_id = fields.Many2one('sekolah.guru', string='Guru', related='jadwal_id.guru_id', store=True)

    status = fields.Selection([
        ('hadir', 'Hadir'),
        ('izin', 'Izin'),
        ('sakit', 'Sakit'),
        ('alfa', 'Alfa')
    ], string='Status', required=True, default='hadir', tracking=True)

    keterangan = fields.Text(string='Keterangan')

    tahun_ajaran_id = fields.Many2one('sekolah.tahun_ajaran', string='Tahun Ajaran')
    semester = fields.Selection(related='tahun_ajaran_id.semester', string='Semester', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('sekolah.absensi') or 'New'
        return super().create(vals_list)

    @api.constrains('siswa_id', 'jadwal_id', 'tanggal')
    def _check_duplicate(self):
        for record in self:
            if record.jadwal_id:
                duplicate = self.search([
                    ('id', '!=', record.id),
                    ('siswa_id', '=', record.siswa_id.id),
                    ('jadwal_id', '=', record.jadwal_id.id),
                    ('tanggal', '=', record.tanggal)
                ])
                if duplicate:
                    raise ValidationError(
                        f'Absensi untuk siswa {record.siswa_id.name} pada jadwal ini '
                        f'di tanggal {record.tanggal} sudah ada!'
                    )
