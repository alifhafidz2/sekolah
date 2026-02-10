from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SppPembayaran(models.Model):
    _name = 'al.spp.pembayaran'
    _description = 'Pembayaran SPP'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'tanggal_bayar desc, id desc'

    name = fields.Char(
        string='Nomor Bukti',
        readonly=True,
        copy=False,
        default='New',
    )
    tagihan_id = fields.Many2one(
        'al.spp.tagihan',
        string='Tagihan',
        required=True,
        tracking=True,
        ondelete='cascade',
    )
    siswa_id = fields.Many2one(
        'sekolah.siswa',
        string='Siswa',
        related='tagihan_id.siswa_id',
        store=True,
    )
    kelas_id = fields.Many2one(
        'sekolah.kelas',
        string='Kelas',
        related='tagihan_id.kelas_id',
        store=True,
    )
    tanggal_bayar = fields.Date(
        string='Tanggal Bayar',
        default=fields.Date.context_today,
        required=True,
        tracking=True,
    )
    nominal = fields.Float(
        string='Nominal Bayar',
        required=True,
        tracking=True,
    )
    metode_bayar = fields.Selection([
        ('tunai', 'Tunai'),
        ('transfer', 'Transfer Bank'),
        ('qris', 'QRIS'),
        ('va', 'Virtual Account'),
    ], string='Metode Pembayaran', default='tunai', required=True, tracking=True)
    bank_id = fields.Selection([
        ('bca', 'BCA'),
        ('bni', 'BNI'),
        ('bri', 'BRI'),
        ('mandiri', 'Mandiri'),
        ('bsi', 'BSI'),
        ('lainnya', 'Lainnya'),
    ], string='Bank')
    no_referensi = fields.Char(
        string='No. Referensi/Transfer',
        tracking=True,
    )
    bukti_bayar = fields.Binary(
        string='Bukti Pembayaran',
        attachment=True,
    )
    bukti_bayar_filename = fields.Char(string='Filename')
    penerima_id = fields.Many2one(
        'res.users',
        string='Diterima Oleh',
        default=lambda self: self.env.user,
        tracking=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Dikonfirmasi'),
        ('cancel', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Catatan')
    bulan_tagihan = fields.Selection(
        related='tagihan_id.bulan',
        string='Bulan',
        store=True,
    )
    tahun_tagihan = fields.Char(
        related='tagihan_id.tahun',
        string='Tahun',
        store=True,
    )
    jenis_tagihan = fields.Selection(
        related='tagihan_id.jenis_tagihan',
        string='Jenis Tagihan',
        store=True,
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('al.spp.pembayaran') or 'New'
        result = super().create(vals)
        return result

    @api.constrains('nominal')
    def _check_nominal(self):
        for rec in self:
            if rec.nominal <= 0:
                raise ValidationError('Nominal pembayaran harus lebih dari 0!')

    @api.constrains('nominal', 'tagihan_id')
    def _check_nominal_vs_sisa(self):
        for rec in self:
            if rec.tagihan_id and rec.state != 'cancel':
                sisa = rec.tagihan_id.sisa_tagihan
                if rec.state == 'draft':
                    sisa = rec.tagihan_id.total_tagihan - sum(
                        p.nominal for p in rec.tagihan_id.pembayaran_ids
                        if p.state == 'confirmed' and p.id != rec.id
                    )
                if rec.nominal > sisa + 0.01:
                    raise ValidationError(
                        f'Nominal pembayaran ({rec.nominal:,.0f}) melebihi sisa tagihan ({sisa:,.0f})!'
                    )

    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'confirmed'
                rec.tagihan_id._update_state()

    def action_cancel(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'cancel'
                rec.tagihan_id._update_state()

    def action_set_to_draft(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.state = 'draft'

    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = f'/my/spp/pembayaran/{rec.id}'

    def action_print_kwitansi(self):
        self.ensure_one()
        return self.env.ref('al_spp_school.action_report_kwitansi').report_action(self)

    def terbilang(self):
        self.ensure_one()
        nominal = int(self.nominal)
        if nominal == 0:
            return "Nol Rupiah"
        satuan = ['', 'Satu', 'Dua', 'Tiga', 'Empat', 'Lima', 'Enam', 'Tujuh', 'Delapan', 'Sembilan', 'Sepuluh', 'Sebelas']
        def _terbilang(n):
            if n < 12:
                return satuan[n]
            elif n < 20:
                return satuan[n - 10] + ' Belas'
            elif n < 100:
                return satuan[n // 10] + ' Puluh ' + satuan[n % 10]
            elif n < 200:
                return 'Seratus ' + _terbilang(n - 100)
            elif n < 1000:
                return satuan[n // 100] + ' Ratus ' + _terbilang(n % 100)
            elif n < 2000:
                return 'Seribu ' + _terbilang(n - 1000)
            elif n < 1000000:
                return _terbilang(n // 1000) + ' Ribu ' + _terbilang(n % 1000)
            elif n < 1000000000:
                return _terbilang(n // 1000000) + ' Juta ' + _terbilang(n % 1000000)
            elif n < 1000000000000:
                return _terbilang(n // 1000000000) + ' Milyar ' + _terbilang(n % 1000000000)
            else:
                return _terbilang(n // 1000000000000) + ' Triliun ' + _terbilang(n % 1000000000000)
        result = _terbilang(nominal)
        result = ' '.join(result.split())
        return result + ' Rupiah'
