from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GenerateJadwalWizard(models.TransientModel):
    _name = 'sekolah.generate.jadwal.wizard'
    _description = 'Wizard Generate Jadwal'

    kelas_id = fields.Many2one('sekolah.kelas', string='Kelas', required=True)
    tahun_ajaran_id = fields.Many2one('sekolah.tahun_ajaran', string='Tahun Ajaran', required=True)

    mata_pelajaran_ids = fields.Many2many('sekolah.mata_pelajaran', string='Mata Pelajaran')

    jam_mulai_default = fields.Float(string='Jam Mulai Default', default=7.0)
    durasi_per_sesi = fields.Float(string='Durasi per Sesi (jam)', default=1.5)
    jam_selesai_default = fields.Float(string='Jam Selesai Harian', default=15.0)

    hari_senin = fields.Boolean(string='Senin', default=True)
    hari_selasa = fields.Boolean(string='Selasa', default=True)
    hari_rabu = fields.Boolean(string='Rabu', default=True)
    hari_kamis = fields.Boolean(string='Kamis', default=True)
    hari_jumat = fields.Boolean(string='Jumat', default=True)
    hari_sabtu = fields.Boolean(string='Sabtu', default=False)

    hapus_jadwal_lama = fields.Boolean(
        string='Hapus Jadwal Lama',
        default=True,
        help='Hapus jadwal yang sudah ada untuk kelas dan hari yang dipilih sebelum generate yang baru',
    )

    istirahat_1 = fields.Boolean(string='Istirahat 1', default=True)
    jam_istirahat_1 = fields.Float(string='Jam Istirahat 1', default=10.0)
    durasi_istirahat_1 = fields.Float(string='Durasi Istirahat 1', default=0.25)

    istirahat_2 = fields.Boolean(string='Istirahat 2 (Siang)', default=True)
    jam_istirahat_2 = fields.Float(string='Jam Istirahat 2', default=12.0)
    durasi_istirahat_2 = fields.Float(string='Durasi Istirahat 2', default=0.5)

    def _get_selected_hari(self):
        hari_list = []
        if self.hari_senin:
            hari_list.append('senin')
        if self.hari_selasa:
            hari_list.append('selasa')
        if self.hari_rabu:
            hari_list.append('rabu')
        if self.hari_kamis:
            hari_list.append('kamis')
        if self.hari_jumat:
            hari_list.append('jumat')
        if self.hari_sabtu:
            hari_list.append('sabtu')
        return hari_list

    def _get_breaks(self):
        breaks = []
        if self.istirahat_1:
            breaks.append((self.jam_istirahat_1, self.durasi_istirahat_1))
        if self.istirahat_2:
            breaks.append((self.jam_istirahat_2, self.durasi_istirahat_2))
        return sorted(breaks, key=lambda b: b[0])

    def _apply_break(self, jam_mulai, breaks_applied, breaks):
        for idx, (break_start, break_duration) in enumerate(breaks):
            if idx not in breaks_applied and jam_mulai >= break_start:
                breaks_applied.add(idx)
                jam_mulai += break_duration
        return jam_mulai

    def action_generate(self):
        self.ensure_one()

        if not self.mata_pelajaran_ids:
            raise ValidationError('Pilih minimal satu mata pelajaran!')

        hari_list = self._get_selected_hari()
        if not hari_list:
            raise ValidationError('Pilih minimal satu hari!')

        jadwal_obj = self.env['sekolah.jadwal']

        if self.hapus_jadwal_lama:
            existing = jadwal_obj.search([
                ('kelas_id', '=', self.kelas_id.id),
                ('tahun_ajaran_id', '=', self.tahun_ajaran_id.id),
                ('hari', 'in', hari_list),
            ])
            if existing:
                existing.unlink()

        breaks = self._get_breaks()

        created_count = 0
        jam_mulai = self.jam_mulai_default
        hari_idx = 0
        jam_ke = 1
        breaks_applied = set()

        for mapel in self.mata_pelajaran_ids:
            if hari_idx >= len(hari_list):
                break

            guru = mapel.guru_ids[0] if mapel.guru_ids else False

            jam_mulai = self._apply_break(jam_mulai, breaks_applied, breaks)
            jam_selesai = jam_mulai + self.durasi_per_sesi

            if jam_selesai > self.jam_selesai_default:
                hari_idx += 1
                jam_mulai = self.jam_mulai_default
                jam_ke = 1
                breaks_applied = set()

                if hari_idx >= len(hari_list):
                    break

                jam_mulai = self._apply_break(jam_mulai, breaks_applied, breaks)
                jam_selesai = jam_mulai + self.durasi_per_sesi

            jadwal_obj.create({
                'kelas_id': self.kelas_id.id,
                'mata_pelajaran_id': mapel.id,
                'guru_id': guru.id if guru else False,
                'hari': hari_list[hari_idx],
                'jam_mulai': jam_mulai,
                'jam_selesai': jam_selesai,
                'jam_ke': jam_ke,
                'tahun_ajaran_id': self.tahun_ajaran_id.id,
            })

            created_count += 1
            jam_mulai = jam_selesai
            jam_ke += 1

            if jam_mulai >= self.jam_selesai_default:
                hari_idx += 1
                jam_mulai = self.jam_mulai_default
                jam_ke = 1
                breaks_applied = set()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': f'{created_count} jadwal berhasil digenerate!',
                'type': 'success',
                'sticky': False,
            }
        }
