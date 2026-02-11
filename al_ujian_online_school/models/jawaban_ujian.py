from odoo import models, fields, api
import re


class JawabanUjian(models.Model):
    _name = 'ujian.jawaban'
    _description = 'Jawaban Ujian'
    _order = 'peserta_id, id'

    peserta_id = fields.Many2one(
        'ujian.peserta',
        string='Peserta',
        required=True,
        ondelete='cascade'
    )
    paket_line_id = fields.Many2one(
        'ujian.paket_soal_line',
        string='Paket Soal Line',
        ondelete='cascade'
    )
    soal_id = fields.Many2one(
        'ujian.bank_soal',
        string='Soal',
        required=True,
        ondelete='restrict'
    )
    tipe_soal = fields.Selection(
        related='soal_id.tipe_soal',
        store=True
    )
    pilihan_id = fields.Many2one(
        'ujian.pilihan_jawaban',
        string='Pilihan (PG)',
        ondelete='set null'
    )
    pilihan_ids = fields.Many2many(
        'ujian.pilihan_jawaban',
        'ujian_jawaban_pilihan_rel',
        'jawaban_id',
        'pilihan_id',
        string='Pilihan (PG Kompleks)'
    )
    jawaban = fields.Text(string='Jawaban (Isian/Essay)')
    is_correct = fields.Boolean(
        string='Benar',
        default=False,
        compute='_compute_correction',
        store=True
    )
    poin_diperoleh = fields.Float(
        string='Poin',
        default=0,
        compute='_compute_correction',
        store=True,
        digits=(10, 2)
    )
    is_ragu = fields.Boolean(string='Ragu-ragu', default=False)
    waktu_jawab = fields.Datetime(string='Waktu Jawab')
    koreksi_manual = fields.Boolean(
        string='Perlu Koreksi Manual',
        compute='_compute_correction',
        store=True
    )
    komentar_guru = fields.Text(string='Komentar Guru')
    poin_manual = fields.Float(string='Poin Manual', digits=(10, 2))

    @api.depends('pilihan_id', 'pilihan_ids', 'jawaban', 'soal_id', 'poin_manual')
    def _compute_correction(self):
        for rec in self:
            if not rec.soal_id:
                rec.is_correct = False
                rec.poin_diperoleh = 0
                rec.koreksi_manual = False
                continue
            tipe = rec.soal_id.tipe_soal
            bobot = rec.soal_id.bobot
            if tipe == 'pg':
                rec.is_correct = rec.pilihan_id and rec.pilihan_id.is_correct
                rec.poin_diperoleh = bobot if rec.is_correct else 0
                rec.koreksi_manual = False
            elif tipe == 'pg_kompleks':
                if rec.pilihan_ids:
                    jawaban_benar = rec.soal_id.pilihan_ids.filtered('is_correct')
                    if set(rec.pilihan_ids.ids) == set(jawaban_benar.ids):
                        rec.is_correct = True
                        rec.poin_diperoleh = bobot
                    else:
                        benar_dipilih = len(set(rec.pilihan_ids.ids) & set(jawaban_benar.ids))
                        salah_dipilih = len(set(rec.pilihan_ids.ids) - set(jawaban_benar.ids))
                        if salah_dipilih > 0:
                            rec.is_correct = False
                            rec.poin_diperoleh = 0
                        else:
                            rec.is_correct = False
                            rec.poin_diperoleh = (benar_dipilih / len(jawaban_benar)) * bobot
                else:
                    rec.is_correct = False
                    rec.poin_diperoleh = 0
                rec.koreksi_manual = False
            elif tipe == 'benar_salah':
                rec.is_correct = rec.pilihan_id and rec.pilihan_id.is_correct
                rec.poin_diperoleh = bobot if rec.is_correct else 0
                rec.koreksi_manual = False
            elif tipe == 'isian':
                if rec.jawaban:
                    jawaban_user = rec.jawaban.strip().lower()
                    jawaban_benar = (rec.soal_id.jawaban_benar or '').strip().lower()
                    jawaban_alt = rec.soal_id.jawaban_benar_alt or ''
                    alt_list = [j.strip().lower() for j in jawaban_alt.split(',') if j.strip()]
                    all_correct = [jawaban_benar] + alt_list
                    rec.is_correct = jawaban_user in all_correct
                    rec.poin_diperoleh = bobot if rec.is_correct else 0
                else:
                    rec.is_correct = False
                    rec.poin_diperoleh = 0
                rec.koreksi_manual = False
            elif tipe == 'essay':
                rec.koreksi_manual = True
                if rec.poin_manual:
                    rec.poin_diperoleh = rec.poin_manual
                    rec.is_correct = rec.poin_manual >= (bobot * 0.5)
                else:
                    rec.is_correct = False
                    rec.poin_diperoleh = 0
            elif tipe == 'menjodohkan':
                rec.koreksi_manual = True
                rec.is_correct = False
                rec.poin_diperoleh = rec.poin_manual or 0
            else:
                rec.is_correct = False
                rec.poin_diperoleh = 0
                rec.koreksi_manual = True

    def action_koreksi_manual(self):
        self.ensure_one()
        return {
            'name': 'Koreksi Manual',
            'type': 'ir.actions.act_window',
            'res_model': 'ujian.jawaban',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def save_answer(self, answer_data):
        self.ensure_one()
        from datetime import datetime
        vals = {'waktu_jawab': datetime.now()}
        if answer_data.get('is_ragu'):
            vals['is_ragu'] = answer_data['is_ragu']
        tipe = self.soal_id.tipe_soal
        if tipe in ['pg', 'benar_salah']:
            pilihan_id = answer_data.get('pilihan_id')
            if pilihan_id:
                vals['pilihan_id'] = int(pilihan_id)
        elif tipe == 'pg_kompleks':
            pilihan_ids = answer_data.get('pilihan_ids', [])
            vals['pilihan_ids'] = [(6, 0, [int(p) for p in pilihan_ids])]
        elif tipe in ['isian', 'essay']:
            vals['jawaban'] = answer_data.get('jawaban', '')
        self.write(vals)
        return True
