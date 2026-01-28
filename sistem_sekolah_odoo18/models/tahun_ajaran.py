from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TahunAjaran(models.Model):
    _name = 'sekolah.tahun_ajaran'
    _description = 'Tahun Ajaran'
    _order = 'tahun_mulai desc, semester desc'

    name = fields.Char(string='Nama', compute='_compute_name', store=True)
    tahun_mulai = fields.Integer(string='Tahun Mulai', required=True)
    tahun_selesai = fields.Integer(string='Tahun Selesai', required=True)
    semester = fields.Selection([
        ('1', 'Ganjil'),
        ('2', 'Genap')
    ], string='Semester', required=True, default='1')
    tanggal_mulai = fields.Date(string='Tanggal Mulai', required=True)
    tanggal_selesai = fields.Date(string='Tanggal Selesai', required=True)
    is_active = fields.Boolean(string='Aktif', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Aktif'),
        ('done', 'Selesai')
    ], string='Status', default='draft', required=True)

    keterangan = fields.Text(string='Keterangan')

    @api.depends('tahun_mulai', 'tahun_selesai', 'semester')
    def _compute_name(self):
        for record in self:
            if record.tahun_mulai and record.tahun_selesai and record.semester:
                semester_text = 'Ganjil' if record.semester == '1' else 'Genap'
                record.name = f"{record.tahun_mulai}/{record.tahun_selesai} - Semester {semester_text}"
            else:
                record.name = 'Tahun Ajaran Baru'

    @api.constrains('tahun_mulai', 'tahun_selesai')
    def _check_tahun(self):
        for record in self:
            if record.tahun_selesai <= record.tahun_mulai:
                raise ValidationError('Tahun selesai harus lebih besar dari tahun mulai!')

    @api.constrains('tanggal_mulai', 'tanggal_selesai')
    def _check_tanggal(self):
        for record in self:
            if record.tanggal_selesai <= record.tanggal_mulai:
                raise ValidationError('Tanggal selesai harus lebih besar dari tanggal mulai!')

    @api.constrains('is_active')
    def _check_active(self):
        for record in self:
            if record.is_active:
                other_active = self.search([
                    ('id', '!=', record.id),
                    ('is_active', '=', True)
                ])
                if other_active:
                    raise ValidationError('Hanya boleh ada satu tahun ajaran aktif!')

    def action_set_active(self):
        self.ensure_one()
        self.env['sekolah.tahun_ajaran'].search([]).write({'is_active': False})
        self.write({'is_active': True, 'state': 'active'})

    def action_set_done(self):
        self.ensure_one()
        self.write({'is_active': False, 'state': 'done'})
