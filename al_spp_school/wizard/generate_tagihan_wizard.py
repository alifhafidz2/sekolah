from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta


class GenerateTagihanWizard(models.TransientModel):
    _name = 'al.spp.generate.tagihan.wizard'
    _description = 'Generate Tagihan SPP Wizard'

    spp_config_id = fields.Many2one(
        'al.spp.config',
        string='Konfigurasi SPP',
        required=True,
    )
    tahun_ajaran_id = fields.Many2one(
        'sekolah.tahun_ajaran',
        string='Tahun Ajaran',
        required=True,
    )
    kelas_id = fields.Many2one(
        'sekolah.kelas',
        string='Kelas',
        required=True,
    )
    jenis_tagihan = fields.Selection([
        ('spp', 'SPP Bulanan'),
        ('daftar_ulang', 'Daftar Ulang'),
        ('kegiatan', 'Biaya Kegiatan'),
        ('seragam', 'Biaya Seragam'),
        ('buku', 'Biaya Buku'),
    ], string='Jenis Tagihan', default='spp', required=True)
    bulan_mulai = fields.Selection([
        ('1', 'Januari'),
        ('2', 'Februari'),
        ('3', 'Maret'),
        ('4', 'April'),
        ('5', 'Mei'),
        ('6', 'Juni'),
        ('7', 'Juli'),
        ('8', 'Agustus'),
        ('9', 'September'),
        ('10', 'Oktober'),
        ('11', 'November'),
        ('12', 'Desember'),
    ], string='Bulan Mulai', default='7')
    bulan_akhir = fields.Selection([
        ('1', 'Januari'),
        ('2', 'Februari'),
        ('3', 'Maret'),
        ('4', 'April'),
        ('5', 'Mei'),
        ('6', 'Juni'),
        ('7', 'Juli'),
        ('8', 'Agustus'),
        ('9', 'September'),
        ('10', 'Oktober'),
        ('11', 'November'),
        ('12', 'Desember'),
    ], string='Bulan Akhir', default='6')
    tahun = fields.Char(
        string='Tahun',
        default=lambda self: str(date.today().year),
        required=True,
    )
    hari_jatuh_tempo = fields.Integer(
        string='Hari Jatuh Tempo',
        default=10,
        help='Tanggal jatuh tempo setiap bulan',
    )
    siswa_ids = fields.Many2many(
        'sekolah.siswa',
        string='Siswa',
        domain="[('kelas_id', '=', kelas_id)]",
    )
    select_all_siswa = fields.Boolean(
        string='Pilih Semua Siswa',
        default=True,
    )

    @api.onchange('kelas_id', 'select_all_siswa')
    def _onchange_kelas(self):
        if self.kelas_id and self.select_all_siswa:
            siswa = self.env['sekolah.siswa'].search([
                ('kelas_id', '=', self.kelas_id.id),
                ('status', '=', 'aktif'),
            ])
            self.siswa_ids = siswa
        elif not self.select_all_siswa:
            self.siswa_ids = False

    def action_generate(self):
        self.ensure_one()

        if not self.siswa_ids:
            if self.select_all_siswa and self.kelas_id:
                siswa_list = self.env['sekolah.siswa'].search([
                    ('kelas_id', '=', self.kelas_id.id),
                    ('status', '=', 'aktif'),
                ])
            else:
                raise UserError('Pilih minimal satu siswa!')
        else:
            siswa_list = self.siswa_ids

        if not siswa_list:
            raise UserError('Tidak ada siswa aktif di kelas ini!')

        Tagihan = self.env['al.spp.tagihan']
        created_count = 0
        skipped_count = 0

        if self.jenis_tagihan == 'spp':
            bulan_mulai = int(self.bulan_mulai)
            bulan_akhir = int(self.bulan_akhir)

            if bulan_mulai <= bulan_akhir:
                bulan_range = range(bulan_mulai, bulan_akhir + 1)
            else:
                bulan_range = list(range(bulan_mulai, 13)) + list(range(1, bulan_akhir + 1))

            for siswa in siswa_list:
                tahun_current = int(self.tahun)
                for bulan in bulan_range:
                    if bulan_mulai > bulan_akhir and bulan < bulan_mulai:
                        tahun_tagihan = tahun_current + 1
                    else:
                        tahun_tagihan = tahun_current

                    existing = Tagihan.search([
                        ('siswa_id', '=', siswa.id),
                        ('tahun_ajaran_id', '=', self.tahun_ajaran_id.id),
                        ('bulan', '=', str(bulan)),
                        ('tahun', '=', str(tahun_tagihan)),
                        ('jenis_tagihan', '=', 'spp'),
                    ], limit=1)

                    if existing:
                        skipped_count += 1
                        continue

                    tanggal_tagihan = date(tahun_tagihan, bulan, 1)
                    tanggal_jatuh_tempo = date(
                        tahun_tagihan, bulan,
                        min(self.hari_jatuh_tempo, 28)
                    )

                    Tagihan.create({
                        'siswa_id': siswa.id,
                        'tahun_ajaran_id': self.tahun_ajaran_id.id,
                        'spp_config_id': self.spp_config_id.id,
                        'bulan': str(bulan),
                        'tahun': str(tahun_tagihan),
                        'tanggal_tagihan': tanggal_tagihan,
                        'tanggal_jatuh_tempo': tanggal_jatuh_tempo,
                        'nominal': self.spp_config_id.nominal_spp,
                        'jenis_tagihan': 'spp',
                        'state': 'open',
                    })
                    created_count += 1
        else:
            nominal_map = {
                'daftar_ulang': self.spp_config_id.nominal_daftar_ulang,
                'kegiatan': self.spp_config_id.nominal_kegiatan,
                'seragam': self.spp_config_id.nominal_seragam,
                'buku': self.spp_config_id.nominal_buku,
            }
            nominal = nominal_map.get(self.jenis_tagihan, 0)

            if nominal <= 0:
                raise UserError(f'Nominal untuk {self.jenis_tagihan} belum dikonfigurasi!')

            for siswa in siswa_list:
                existing = Tagihan.search([
                    ('siswa_id', '=', siswa.id),
                    ('tahun_ajaran_id', '=', self.tahun_ajaran_id.id),
                    ('jenis_tagihan', '=', self.jenis_tagihan),
                ], limit=1)

                if existing:
                    skipped_count += 1
                    continue

                tanggal_tagihan = date.today()
                tanggal_jatuh_tempo = tanggal_tagihan + relativedelta(days=30)

                Tagihan.create({
                    'siswa_id': siswa.id,
                    'tahun_ajaran_id': self.tahun_ajaran_id.id,
                    'spp_config_id': self.spp_config_id.id,
                    'bulan': str(tanggal_tagihan.month),
                    'tahun': str(tanggal_tagihan.year),
                    'tanggal_tagihan': tanggal_tagihan,
                    'tanggal_jatuh_tempo': tanggal_jatuh_tempo,
                    'nominal': nominal,
                    'jenis_tagihan': self.jenis_tagihan,
                    'state': 'open',
                })
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Generate Tagihan Selesai',
                'message': f'Berhasil membuat {created_count} tagihan. {skipped_count} tagihan dilewati (sudah ada).',
                'type': 'success',
                'sticky': False,
            }
        }
