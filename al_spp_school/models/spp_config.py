from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SppConfig(models.Model):
    _name = 'al.spp.config'
    _description = 'Konfigurasi SPP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tahun_ajaran_id desc, kelas_id'

    name = fields.Char(
        string='Nama',
        compute='_compute_name',
        store=True,
    )
    tahun_ajaran_id = fields.Many2one(
        'sekolah.tahun_ajaran',
        string='Tahun Ajaran',
        required=True,
        tracking=True,
    )
    kelas_id = fields.Many2one(
        'sekolah.kelas',
        string='Kelas',
        required=True,
        tracking=True,
    )
    nominal_spp = fields.Float(
        string='Nominal SPP',
        required=True,
        tracking=True,
        help='Nominal SPP per bulan',
    )
    nominal_daftar_ulang = fields.Float(
        string='Daftar Ulang',
        tracking=True,
        help='Biaya daftar ulang tahunan',
    )
    nominal_kegiatan = fields.Float(
        string='Biaya Kegiatan',
        tracking=True,
        help='Biaya kegiatan per semester',
    )
    nominal_seragam = fields.Float(
        string='Biaya Seragam',
        tracking=True,
    )
    nominal_buku = fields.Float(
        string='Biaya Buku',
        tracking=True,
    )
    total_biaya_tahunan = fields.Float(
        string='Total Biaya Tahunan',
        compute='_compute_total_biaya',
        store=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    notes = fields.Text(
        string='Catatan',
    )

    _sql_constraints = [
        ('unique_config', 'unique(tahun_ajaran_id, kelas_id)',
         'Konfigurasi SPP untuk tahun ajaran dan kelas ini sudah ada!'),
    ]

    @api.depends('tahun_ajaran_id', 'kelas_id')
    def _compute_name(self):
        for rec in self:
            if rec.tahun_ajaran_id and rec.kelas_id:
                rec.name = f"SPP {rec.kelas_id.name} - {rec.tahun_ajaran_id.name}"
            else:
                rec.name = "New"

    @api.depends('nominal_spp', 'nominal_daftar_ulang', 'nominal_kegiatan',
                 'nominal_seragam', 'nominal_buku')
    def _compute_total_biaya(self):
        for rec in self:
            spp_tahunan = rec.nominal_spp * 12
            rec.total_biaya_tahunan = (
                spp_tahunan +
                rec.nominal_daftar_ulang +
                rec.nominal_kegiatan +
                rec.nominal_seragam +
                rec.nominal_buku
            )

    @api.constrains('nominal_spp')
    def _check_nominal_spp(self):
        for rec in self:
            if rec.nominal_spp <= 0:
                raise ValidationError('Nominal SPP harus lebih dari 0!')

    def action_generate_tagihan(self):
        self.ensure_one()
        return {
            'name': 'Generate Tagihan SPP',
            'type': 'ir.actions.act_window',
            'res_model': 'al.spp.generate.tagihan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_spp_config_id': self.id,
                'default_tahun_ajaran_id': self.tahun_ajaran_id.id,
                'default_kelas_id': self.kelas_id.id,
            },
        }
