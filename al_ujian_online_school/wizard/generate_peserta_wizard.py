from odoo import models, fields, api
from odoo.exceptions import UserError


class GeneratePesertaWizard(models.TransientModel):
    _name = 'ujian.generate_peserta_wizard'
    _description = 'Generate Peserta Ujian'

    paket_id = fields.Many2one(
        'ujian.paket',
        string='Paket Ujian',
        required=True,
        ondelete='cascade'
    )
    kelas_ids = fields.Many2many(
        'sekolah.kelas',
        string='Kelas',
        related='paket_id.kelas_ids',
        readonly=True
    )
    siswa_ids = fields.Many2many(
        'sekolah.siswa',
        string='Siswa Terpilih',
        compute='_compute_siswa_ids',
        store=True,
        readonly=False
    )
    jumlah_siswa = fields.Integer(
        string='Jumlah Siswa',
        compute='_compute_jumlah_siswa'
    )
    replace_existing = fields.Boolean(
        string='Ganti Peserta yang Ada',
        default=False,
        help='Jika dicentang, peserta yang sudah ada akan dihapus dan diganti dengan yang baru'
    )

    @api.depends('paket_id', 'paket_id.kelas_ids')
    def _compute_siswa_ids(self):
        for rec in self:
            if rec.paket_id and rec.paket_id.kelas_ids:
                siswa = self.env['sekolah.siswa'].search([
                    ('kelas_id', 'in', rec.paket_id.kelas_ids.ids),
                    ('active', '=', True)
                ])
                rec.siswa_ids = siswa.ids
            else:
                rec.siswa_ids = []

    @api.depends('siswa_ids')
    def _compute_jumlah_siswa(self):
        for rec in self:
            rec.jumlah_siswa = len(rec.siswa_ids)

    def action_generate(self):
        self.ensure_one()
        if not self.siswa_ids:
            raise UserError('Tidak ada siswa yang dipilih!')
        if self.replace_existing:
            self.paket_id.peserta_ids.filtered(lambda p: p.state == 'belum').unlink()
        existing_siswa = self.paket_id.peserta_ids.mapped('siswa_id').ids
        peserta_vals = []
        for siswa in self.siswa_ids:
            if siswa.id not in existing_siswa:
                peserta_vals.append({
                    'paket_id': self.paket_id.id,
                    'siswa_id': siswa.id,
                })
        if peserta_vals:
            self.env['ujian.peserta'].create(peserta_vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Berhasil',
                'message': f'{len(peserta_vals)} peserta berhasil ditambahkan',
                'type': 'success',
                'sticky': False,
            }
        }
