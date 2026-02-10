from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class SppTagihan(models.Model):
    _name = 'al.spp.tagihan'
    _description = 'Tagihan SPP'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'tahun desc, bulan desc, siswa_id'

    name = fields.Char(
        string='Nomor Tagihan',
        readonly=True,
        copy=False,
        default='New',
    )
    siswa_id = fields.Many2one(
        'sekolah.siswa',
        string='Siswa',
        required=True,
        tracking=True,
        ondelete='cascade',
    )
    kelas_id = fields.Many2one(
        'sekolah.kelas',
        string='Kelas',
        related='siswa_id.kelas_id',
        store=True,
    )
    tahun_ajaran_id = fields.Many2one(
        'sekolah.tahun_ajaran',
        string='Tahun Ajaran',
        required=True,
        tracking=True,
    )
    spp_config_id = fields.Many2one(
        'al.spp.config',
        string='Konfigurasi SPP',
        tracking=True,
    )
    bulan = fields.Selection([
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
    ], string='Bulan', required=True, tracking=True)
    tahun = fields.Char(
        string='Tahun',
        required=True,
        tracking=True,
    )
    tanggal_tagihan = fields.Date(
        string='Tanggal Tagihan',
        default=fields.Date.context_today,
        required=True,
    )
    tanggal_jatuh_tempo = fields.Date(
        string='Jatuh Tempo',
        required=True,
        tracking=True,
    )
    nominal = fields.Float(
        string='Nominal Tagihan',
        required=True,
        tracking=True,
    )
    nominal_denda = fields.Float(
        string='Denda',
        compute='_compute_denda',
        store=True,
    )
    total_tagihan = fields.Float(
        string='Total Tagihan',
        compute='_compute_total',
        store=True,
    )
    nominal_terbayar = fields.Float(
        string='Terbayar',
        compute='_compute_terbayar',
        store=True,
    )
    sisa_tagihan = fields.Float(
        string='Sisa Tagihan',
        compute='_compute_sisa',
        store=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Belum Lunas'),
        ('partial', 'Sebagian'),
        ('paid', 'Lunas'),
        ('cancel', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True)
    pembayaran_ids = fields.One2many(
        'al.spp.pembayaran',
        'tagihan_id',
        string='Pembayaran',
    )
    jenis_tagihan = fields.Selection([
        ('spp', 'SPP Bulanan'),
        ('daftar_ulang', 'Daftar Ulang'),
        ('kegiatan', 'Biaya Kegiatan'),
        ('seragam', 'Biaya Seragam'),
        ('buku', 'Biaya Buku'),
        ('lainnya', 'Lainnya'),
    ], string='Jenis Tagihan', default='spp', required=True)
    notes = fields.Text(string='Catatan')
    is_overdue = fields.Boolean(
        string='Jatuh Tempo Lewat',
        compute='_compute_overdue',
        store=True,
    )

    _sql_constraints = [
        ('unique_tagihan', 'unique(siswa_id, tahun_ajaran_id, bulan, tahun, jenis_tagihan)',
         'Tagihan untuk siswa, bulan, tahun, dan jenis ini sudah ada!'),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('al.spp.tagihan') or 'New'
        return super().create(vals)

    @api.depends('tanggal_jatuh_tempo', 'state')
    def _compute_overdue(self):
        today = date.today()
        for rec in self:
            rec.is_overdue = (
                rec.tanggal_jatuh_tempo and
                rec.tanggal_jatuh_tempo < today and
                rec.state in ['open', 'partial']
            )

    @api.depends('is_overdue', 'tanggal_jatuh_tempo')
    def _compute_denda(self):
        for rec in self:
            if rec.is_overdue and rec.tanggal_jatuh_tempo:
                days_late = (date.today() - rec.tanggal_jatuh_tempo).days
                rec.nominal_denda = min(days_late * 5000, 100000)
            else:
                rec.nominal_denda = 0

    @api.depends('nominal', 'nominal_denda')
    def _compute_total(self):
        for rec in self:
            rec.total_tagihan = rec.nominal + rec.nominal_denda

    @api.depends('pembayaran_ids', 'pembayaran_ids.nominal', 'pembayaran_ids.state')
    def _compute_terbayar(self):
        for rec in self:
            rec.nominal_terbayar = sum(
                p.nominal for p in rec.pembayaran_ids
                if p.state == 'confirmed'
            )

    @api.depends('total_tagihan', 'nominal_terbayar')
    def _compute_sisa(self):
        for rec in self:
            rec.sisa_tagihan = rec.total_tagihan - rec.nominal_terbayar

    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'open'

    def action_cancel(self):
        for rec in self:
            if rec.state in ['draft', 'open']:
                rec.state = 'cancel'

    def action_set_to_draft(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.state = 'draft'

    def _update_state(self):
        for rec in self:
            if rec.state in ['open', 'partial']:
                if rec.sisa_tagihan <= 0:
                    rec.state = 'paid'
                elif rec.nominal_terbayar > 0:
                    rec.state = 'partial'
                else:
                    rec.state = 'open'

    def action_bayar(self):
        self.ensure_one()
        return {
            'name': 'Pembayaran SPP',
            'type': 'ir.actions.act_window',
            'res_model': 'al.spp.pembayaran',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tagihan_id': self.id,
                'default_siswa_id': self.siswa_id.id,
                'default_nominal': self.sisa_tagihan,
            },
        }

    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = f'/my/spp/tagihan/{rec.id}'

    def _get_portal_return_action(self):
        self.ensure_one()
        return self.env.ref('al_spp_school.action_spp_tagihan')
