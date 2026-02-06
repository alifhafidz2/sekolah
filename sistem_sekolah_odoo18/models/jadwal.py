from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Jadwal(models.Model):
    _name = 'sekolah.jadwal'
    _description = 'Jadwal Pelajaran'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'hari, jam_mulai'

    name = fields.Char(string='Kode Jadwal', compute='_compute_name', store=True)

    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas', required=True, tracking=True)
    mata_pelajaran_id = fields.Many2one('sekolah.mata_pelajaran', string='Mata Pelajaran', required=True, tracking=True)
    guru_id = fields.Many2one('sekolah.guru', string='Guru', required=True, tracking=True)

    hari = fields.Selection([
        ('senin', 'Senin'),
        ('selasa', 'Selasa'),
        ('rabu', 'Rabu'),
        ('kamis', 'Kamis'),
        ('jumat', 'Jumat'),
        ('sabtu', 'Sabtu')
    ], string='Hari', required=True, tracking=True)

    jam_mulai = fields.Float(string='Jam Mulai', required=True)
    jam_selesai = fields.Float(string='Jam Selesai', required=True)
    durasi = fields.Float(string='Durasi (jam)', compute='_compute_durasi', store=True)

    jam_ke = fields.Integer(string='Jam Ke-')

    break_before_start = fields.Float(string='Istirahat Mulai')
    break_before_end = fields.Float(string='Istirahat Selesai')

    ruangan = fields.Char(string='Ruangan')

    tahun_ajaran_id = fields.Many2one('sekolah.tahun_ajaran', string='Tahun Ajaran')
    semester = fields.Selection(related='tahun_ajaran_id.semester', string='Semester', store=True)

    keterangan = fields.Text(string='Keterangan')

    active = fields.Boolean(string='Active', default=True)

    @api.depends('kelas_id', 'mata_pelajaran_id', 'hari', 'jam_mulai')
    def _compute_name(self):
        for record in self:
            if record.kelas_id and record.mata_pelajaran_id and record.hari:
                record.name = f"{record.kelas_id.name} - {record.mata_pelajaran_id.name} ({record.hari.capitalize()})"
            else:
                record.name = 'Jadwal Baru'

    @api.depends('jam_mulai', 'jam_selesai')
    def _compute_durasi(self):
        for record in self:
            if record.jam_mulai and record.jam_selesai:
                record.durasi = record.jam_selesai - record.jam_mulai
            else:
                record.durasi = 0.0

    @api.constrains('jam_mulai', 'jam_selesai')
    def _check_jam(self):
        for record in self:
            if record.jam_selesai <= record.jam_mulai:
                raise ValidationError('Jam selesai harus lebih besar dari jam mulai!')
            if record.jam_mulai < 0 or record.jam_mulai > 24:
                raise ValidationError('Jam mulai harus antara 0-24!')
            if record.jam_selesai < 0 or record.jam_selesai > 24:
                raise ValidationError('Jam selesai harus antara 0-24!')

    @api.constrains('guru_id', 'hari', 'jam_mulai', 'jam_selesai')
    def _check_guru_conflict(self):
        for record in self:
            conflicting = self.search([
                ('id', '!=', record.id),
                ('guru_id', '=', record.guru_id.id),
                ('hari', '=', record.hari),
                ('jam_mulai', '<', record.jam_selesai),
                ('jam_selesai', '>', record.jam_mulai),
                ('active', '=', True)
            ])
            if conflicting:
                raise ValidationError(
                    f'Guru {record.guru_id.name} sudah memiliki jadwal di hari {record.hari} '
                    f'pada jam yang bentrok!'
                )

    @api.constrains('kelas_id', 'hari', 'jam_mulai', 'jam_selesai')
    def _check_kelas_conflict(self):
        for record in self:
            conflicting = self.search([
                ('id', '!=', record.id),
                ('kelas_id', '=', record.kelas_id.id),
                ('hari', '=', record.hari),
                ('jam_mulai', '<', record.jam_selesai),
                ('jam_selesai', '>', record.jam_mulai),
                ('active', '=', True)
            ])
            if conflicting:
                raise ValidationError(
                    f'Kelas {record.kelas_id.name} sudah memiliki jadwal di hari {record.hari} '
                    f'pada jam yang bentrok!'
                )

    def _float_to_time_string(self, float_time):
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def get_display_time(self):
        self.ensure_one()
        return f"{self._float_to_time_string(self.jam_mulai)} - {self._float_to_time_string(self.jam_selesai)}"
