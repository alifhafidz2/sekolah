from odoo import models, fields, api


class KategoriSoal(models.Model):
    _name = 'ujian.kategori_soal'
    _description = 'Kategori Soal'
    _order = 'name'

    name = fields.Char(string='Nama Kategori', required=True)
    code = fields.Char(string='Kode', required=True)
    mata_pelajaran_id = fields.Many2one(
        'sekolah.mata_pelajaran',
        string='Mata Pelajaran',
        required=True,
        ondelete='restrict'
    )
    parent_id = fields.Many2one(
        'ujian.kategori_soal',
        string='Kategori Induk',
        ondelete='cascade'
    )
    child_ids = fields.One2many(
        'ujian.kategori_soal',
        'parent_id',
        string='Sub Kategori'
    )
    description = fields.Text(string='Deskripsi')
    soal_count = fields.Integer(
        string='Jumlah Soal',
        compute='_compute_soal_count',
        store=True
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Kode kategori harus unik!')
    ]

    @api.depends('child_ids')
    def _compute_soal_count(self):
        for rec in self:
            rec.soal_count = self.env['ujian.bank_soal'].search_count([
                ('kategori_id', '=', rec.id)
            ])

    def name_get(self):
        result = []
        for rec in self:
            if rec.parent_id:
                name = f"{rec.parent_id.name} / {rec.name}"
            else:
                name = rec.name
            result.append((rec.id, name))
        return result
