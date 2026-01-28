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

    def action_generate(self):
        self.ensure_one()

        if not self.mata_pelajaran_ids:
            raise ValidationError('Pilih minimal satu mata pelajaran!')

        jadwal_obj = self.env['sekolah.jadwal']
        hari_list = ['senin', 'selasa', 'rabu', 'kamis', 'jumat']

        created_count = 0
        jam_mulai = self.jam_mulai_default
        hari_idx = 0
        jam_ke = 1

        for mapel in self.mata_pelajaran_ids:
            if hari_idx >= len(hari_list):
                break

            guru = mapel.guru_ids[0] if mapel.guru_ids else False

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

            if jam_mulai >= 15.0:
                hari_idx += 1
                jam_mulai = self.jam_mulai_default
                jam_ke = 1

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
