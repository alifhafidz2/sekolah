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

    total_siswa = fields.Integer(string='Total Siswa', compute='_compute_statistics')
    total_hadir = fields.Integer(string='Hadir', compute='_compute_statistics')
    total_izin = fields.Integer(string='Izin', compute='_compute_statistics')
    total_sakit = fields.Integer(string='Sakit', compute='_compute_statistics')
    total_alfa = fields.Integer(string='Alfa', compute='_compute_statistics')

    @api.depends('line_ids', 'line_ids.is_hadir', 'line_ids.is_izin', 'line_ids.is_sakit')
    def _compute_statistics(self):
        for wizard in self:
            wizard.total_siswa = len(wizard.line_ids)
            wizard.total_hadir = len(wizard.line_ids.filtered(lambda l: l.is_hadir and not l.is_izin and not l.is_sakit))
            wizard.total_izin = len(wizard.line_ids.filtered(lambda l: l.is_izin))
            wizard.total_sakit = len(wizard.line_ids.filtered(lambda l: l.is_sakit))
            wizard.total_alfa = len(wizard.line_ids.filtered(lambda l: not l.is_hadir and not l.is_izin and not l.is_sakit))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        context = self._context
        if context.get('default_jadwal_id'):
            jadwal = self.env['sekolah.jadwal'].browse(context['default_jadwal_id'])
            if jadwal.exists() and jadwal.kelas_id:
                res['kelas_id'] = jadwal.kelas_id.id
                siswa_list = self.env['sekolah.siswa'].search([
                    ('kelas_id', '=', jadwal.kelas_id.id),
                    ('status', '=', 'aktif')
                ], order='name')
                lines = []
                for idx, siswa in enumerate(siswa_list, 1):
                    lines.append((0, 0, {
                        'siswa_id': siswa.id,
                        'nomor_urut': idx,
                        'is_hadir': True,
                    }))
                res['line_ids'] = lines
        return res

    @api.onchange('kelas_id')
    def _onchange_kelas_id(self):
        if self.kelas_id and not self._context.get('default_jadwal_id'):
            self.line_ids = [(5, 0, 0)]
            siswa_list = self.env['sekolah.siswa'].search([
                ('kelas_id', '=', self.kelas_id.id),
                ('status', '=', 'aktif')
            ], order='name')
            lines = []
            for idx, siswa in enumerate(siswa_list, 1):
                lines.append((0, 0, {
                    'siswa_id': siswa.id,
                    'nomor_urut': idx,
                    'is_hadir': True,
                }))
            self.line_ids = lines

    def action_set_all_hadir(self):
        self.ensure_one()
        if self.line_ids:
            self.line_ids.write({
                'is_hadir': True,
                'is_izin': False,
                'is_sakit': False,
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_set_all_alfa(self):
        self.ensure_one()
        if self.line_ids:
            self.line_ids.write({
                'is_hadir': False,
                'is_izin': False,
                'is_sakit': False,
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_create_absensi(self):
        self.ensure_one()

        if not self.line_ids:
            raise ValidationError('Tidak ada siswa untuk diabsen!')

        invalid_lines = self.line_ids.filtered(lambda l: not l.siswa_id)
        if invalid_lines:
            raise ValidationError('Semua baris harus memiliki siswa!')

        absensi_obj = self.env['sekolah.absensi']
        created_count = 0

        for line in self.line_ids:
            existing = absensi_obj.search([
                ('siswa_id', '=', line.siswa_id.id),
                ('jadwal_id', '=', self.jadwal_id.id),
                ('tanggal', '=', self.tanggal)
            ])

            status = line.get_status()

            if not existing:
                absensi_obj.create({
                    'siswa_id': line.siswa_id.id,
                    'jadwal_id': self.jadwal_id.id,
                    'tanggal': self.tanggal,
                    'status': status,
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

    wizard_id = fields.Many2one('sekolah.absensi.massal.wizard', string='Wizard', ondelete='cascade')
    siswa_id = fields.Many2one('sekolah.siswa', string='Siswa')
    nomor_urut = fields.Integer(string='No')
    nis = fields.Char(related='siswa_id.nis', string='NIS', readonly=True)

    is_hadir = fields.Boolean(string='Hadir', default=True)
    is_izin = fields.Boolean(string='Izin', default=False)
    is_sakit = fields.Boolean(string='Sakit', default=False)

    status_display = fields.Char(string='Status', compute='_compute_status_display')
    keterangan = fields.Char(string='Keterangan')

    @api.depends('is_hadir', 'is_izin', 'is_sakit')
    def _compute_status_display(self):
        for line in self:
            if line.is_izin:
                line.status_display = 'Izin'
            elif line.is_sakit:
                line.status_display = 'Sakit'
            elif line.is_hadir:
                line.status_display = 'Hadir'
            else:
                line.status_display = 'Alfa'

    def get_status(self):
        if self.is_izin:
            return 'izin'
        elif self.is_sakit:
            return 'sakit'
        elif self.is_hadir:
            return 'hadir'
        else:
            return 'alfa'

    @api.onchange('is_hadir')
    def _onchange_is_hadir(self):
        if self.is_hadir:
            self.is_izin = False
            self.is_sakit = False

    @api.onchange('is_izin')
    def _onchange_is_izin(self):
        if self.is_izin:
            self.is_hadir = False
            self.is_sakit = False

    @api.onchange('is_sakit')
    def _onchange_is_sakit(self):
        if self.is_sakit:
            self.is_hadir = False
            self.is_izin = False
