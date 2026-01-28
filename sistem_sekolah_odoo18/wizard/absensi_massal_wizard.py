from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AbsensiMassalWizard(models.TransientModel):
    _name = 'sekolah.absensi.massal.wizard'
    _description = 'Wizard Input Absensi Massal'

    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas', required=True)
    jadwal_id = fields.Many2one('sekolah.jadwal', string='Jadwal/Mata Pelajaran', required=True)
    tanggal = fields.Date(string='Tanggal', required=True, default=fields.Date.today)
    tahun_ajaran_id = fields.Many2one('sekolah.tahun_ajaran', string='Tahun Ajaran')

    line_ids = fields.One2many('sekolah.absensi.massal.wizard.line', 'wizard_id', string='Daftar Siswa')

    @api.onchange('kelas_id')
    def _onchange_kelas_id(self):
        if self.kelas_id:
            self.line_ids = False
            siswa_list = self.env['sekolah.siswa'].search([
                ('kelas_id', '=', self.kelas_id.id),
                ('status', '=', 'aktif')
            ], order='name')

            lines = []
            for siswa in siswa_list:
                lines.append((0, 0, {
                    'siswa_id': siswa.id,
                    'status': 'hadir',
                }))
            self.line_ids = lines

    def action_create_absensi(self):
        self.ensure_one()

        if not self.line_ids:
            raise ValidationError('Tidak ada siswa untuk diabsen!')

        absensi_obj = self.env['sekolah.absensi']
        created_count = 0

        for line in self.line_ids:
            existing = absensi_obj.search([
                ('siswa_id', '=', line.siswa_id.id),
                ('jadwal_id', '=', self.jadwal_id.id),
                ('tanggal', '=', self.tanggal)
            ])

            if not existing:
                absensi_obj.create({
                    'siswa_id': line.siswa_id.id,
                    'jadwal_id': self.jadwal_id.id,
                    'tanggal': self.tanggal,
                    'status': line.status,
                    'keterangan': line.keterangan,
                    'tahun_ajaran_id': self.tahun_ajaran_id.id if self.tahun_ajaran_id else False,
                })
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': f'{created_count} data absensi berhasil dibuat!',
                'type': 'success',
                'sticky': False,
            }
        }


class AbsensiMassalWizardLine(models.TransientModel):
    _name = 'sekolah.absensi.massal.wizard.line'
    _description = 'Line Wizard Absensi Massal'

    wizard_id = fields.Many2one('sekolah.absensi.massal.wizard', string='Wizard', required=True, ondelete='cascade')
    siswa_id = fields.Many2one('sekolah.siswa', string='Siswa', required=True)
    status = fields.Selection([
        ('hadir', 'Hadir'),
        ('izin', 'Izin'),
        ('sakit', 'Sakit'),
        ('alfa', 'Alfa')
    ], string='Status', required=True, default='hadir')
    keterangan = fields.Char(string='Keterangan')
