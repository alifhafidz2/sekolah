from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BankSoal(models.Model):
    _name = 'ujian.bank_soal'
    _description = 'Bank Soal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Kode Soal',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )
    kategori_id = fields.Many2one(
        'ujian.kategori_soal',
        string='Kategori',
        required=True,
        ondelete='restrict',
        tracking=True
    )
    mata_pelajaran_id = fields.Many2one(
        related='kategori_id.mata_pelajaran_id',
        store=True,
        string='Mata Pelajaran'
    )
    tipe_soal = fields.Selection([
        ('pg', 'Pilihan Ganda'),
        ('pg_kompleks', 'Pilihan Ganda Kompleks'),
        ('benar_salah', 'Benar/Salah'),
        ('isian', 'Isian Singkat'),
        ('essay', 'Essay'),
        ('menjodohkan', 'Menjodohkan'),
    ], string='Tipe Soal', required=True, default='pg', tracking=True)
    tingkat_kesulitan = fields.Selection([
        ('mudah', 'Mudah'),
        ('sedang', 'Sedang'),
        ('sulit', 'Sulit'),
    ], string='Tingkat Kesulitan', required=True, default='sedang', tracking=True)
    pertanyaan = fields.Html(string='Pertanyaan', required=True, sanitize=True)
    gambar = fields.Binary(string='Gambar Soal')
    gambar_filename = fields.Char(string='Nama File Gambar')
    pilihan_ids = fields.One2many(
        'ujian.pilihan_jawaban',
        'soal_id',
        string='Pilihan Jawaban'
    )
    jawaban_benar = fields.Text(string='Jawaban Benar (Isian/Essay)')
    jawaban_benar_alt = fields.Text(
        string='Jawaban Alternatif',
        help='Pisahkan dengan koma untuk beberapa jawaban yang diterima'
    )
    bobot = fields.Float(string='Bobot/Poin', default=1.0, required=True)
    pembahasan = fields.Html(string='Pembahasan', sanitize=True)
    kelas_ids = fields.Many2many(
        'sekolah.kelas',
        'ujian_soal_kelas_rel',
        'soal_id',
        'kelas_id',
        string='Untuk Kelas'
    )
    guru_id = fields.Many2one(
        'sekolah.guru',
        string='Dibuat Oleh Guru',
        ondelete='set null'
    )
    is_active = fields.Boolean(string='Aktif', default=True)
    used_count = fields.Integer(
        string='Digunakan',
        compute='_compute_used_count',
        help='Jumlah paket ujian yang menggunakan soal ini'
    )
    correct_rate = fields.Float(
        string='Tingkat Kebenaran (%)',
        compute='_compute_statistics',
        digits=(5, 2),
        help='Persentase siswa yang menjawab benar'
    )
    discrimination_index = fields.Float(
        string='Daya Beda',
        compute='_compute_statistics',
        digits=(5, 3),
        help='Indeks daya beda soal'
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('ujian.bank_soal') or 'New'
        return super().create(vals_list)

    def _compute_used_count(self):
        for rec in self:
            rec.used_count = self.env['ujian.paket_soal_line'].search_count([
                ('soal_id', '=', rec.id)
            ])

    def _compute_statistics(self):
        for rec in self:
            jawaban = self.env['ujian.jawaban'].search([
                ('soal_id', '=', rec.id),
                ('peserta_id.state', '=', 'selesai')
            ])
            if jawaban:
                benar = len(jawaban.filtered(lambda j: j.is_correct))
                rec.correct_rate = (benar / len(jawaban)) * 100
                rec.discrimination_index = rec._calculate_discrimination(jawaban)
            else:
                rec.correct_rate = 0
                rec.discrimination_index = 0

    def _calculate_discrimination(self, jawaban):
        if len(jawaban) < 10:
            return 0
        peserta_scores = {}
        for j in jawaban:
            if j.peserta_id.id not in peserta_scores:
                peserta_scores[j.peserta_id.id] = {
                    'total': j.peserta_id.nilai,
                    'correct': j.is_correct
                }
        sorted_peserta = sorted(peserta_scores.items(), key=lambda x: x[1]['total'], reverse=True)
        n = len(sorted_peserta)
        upper_group = sorted_peserta[:n//3]
        lower_group = sorted_peserta[-n//3:]
        if not upper_group or not lower_group:
            return 0
        upper_correct = sum(1 for p in upper_group if p[1]['correct'])
        lower_correct = sum(1 for p in lower_group if p[1]['correct'])
        return (upper_correct - lower_correct) / len(upper_group)

    @api.constrains('tipe_soal', 'pilihan_ids')
    def _check_pilihan(self):
        for rec in self:
            if rec.tipe_soal in ['pg', 'pg_kompleks', 'benar_salah', 'menjodohkan']:
                if not rec.pilihan_ids:
                    raise ValidationError('Soal tipe ini memerlukan pilihan jawaban!')
                if rec.tipe_soal == 'pg' and len(rec.pilihan_ids.filtered('is_correct')) != 1:
                    raise ValidationError('Pilihan ganda harus memiliki tepat 1 jawaban benar!')
                if rec.tipe_soal == 'benar_salah' and len(rec.pilihan_ids) != 2:
                    raise ValidationError('Soal Benar/Salah harus memiliki 2 pilihan!')

    def action_view_statistics(self):
        self.ensure_one()
        return {
            'name': 'Statistik Soal',
            'type': 'ir.actions.act_window',
            'res_model': 'ujian.jawaban',
            'view_mode': 'list,pivot,graph',
            'domain': [('soal_id', '=', self.id)],
            'context': {'search_default_group_by_benar': 1}
        }


class PilihanJawaban(models.Model):
    _name = 'ujian.pilihan_jawaban'
    _description = 'Pilihan Jawaban'
    _order = 'sequence, id'

    soal_id = fields.Many2one(
        'ujian.bank_soal',
        string='Soal',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Urutan', default=10)
    label = fields.Char(
        string='Label',
        compute='_compute_label',
        store=True
    )
    teks = fields.Html(string='Teks Pilihan', required=True, sanitize=True)
    gambar = fields.Binary(string='Gambar')
    is_correct = fields.Boolean(string='Jawaban Benar', default=False)
    pasangan_id = fields.Many2one(
        'ujian.pilihan_jawaban',
        string='Pasangan (Menjodohkan)',
        ondelete='set null'
    )

    @api.depends('sequence', 'soal_id')
    def _compute_label(self):
        labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for soal in self.mapped('soal_id'):
            pilihan = self.filtered(lambda p: p.soal_id == soal).sorted('sequence')
            for idx, pil in enumerate(pilihan):
                pil.label = labels[idx] if idx < len(labels) else str(idx + 1)
