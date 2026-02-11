from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from datetime import datetime
import json
import pytz


def format_datetime_tz(dt, user_tz=None, format_str='%d %B %Y %H:%M'):
    if not dt:
        return '-'
    if not user_tz:
        user_tz = request.env.user.tz or 'Asia/Jakarta'
    try:
        tz = pytz.timezone(user_tz)
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)
        local_dt = dt.astimezone(tz)
        return local_dt.strftime(format_str)
    except Exception:
        return dt.strftime(format_str) if dt else '-'


class UjianPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'ujian_count' in counters:
            siswa = request.env['sekolah.siswa'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            if siswa:
                values['ujian_count'] = request.env['ujian.peserta'].sudo().search_count([
                    ('siswa_id', '=', siswa.id)
                ])
            else:
                values['ujian_count'] = 0
        return values

    @http.route(['/my/ujian', '/my/ujian/page/<int:page>'], type='http', auth='user', website=True)
    def portal_ujian_list(self, page=1, **kw):
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if not siswa:
            return request.render('al_ujian_online_school.portal_no_siswa', {})
        domain = [('siswa_id', '=', siswa.id)]
        peserta_count = request.env['ujian.peserta'].sudo().search_count(domain)
        pager = portal_pager(
            url='/my/ujian',
            total=peserta_count,
            page=page,
            step=10,
        )
        peserta_list = request.env['ujian.peserta'].sudo().search(
            domain,
            order='create_date desc',
            limit=10,
            offset=pager['offset']
        )
        now = fields.Datetime.now()
        values = {
            'peserta_list': peserta_list,
            'pager': pager,
            'now': now,
            'siswa': siswa,
            'format_datetime_tz': format_datetime_tz,
        }
        return request.render('al_ujian_online_school.portal_ujian_list', values)

    @http.route('/my/ujian/<int:peserta_id>', type='http', auth='user', website=True)
    def portal_ujian_detail(self, peserta_id, **kw):
        peserta = request.env['ujian.peserta'].sudo().browse(peserta_id)
        if not peserta.exists():
            return request.redirect('/my/ujian')
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if peserta.siswa_id.id != siswa.id:
            return request.redirect('/my/ujian')
        paket = peserta.paket_id
        now = fields.Datetime.now()
        can_start = (
            paket.state == 'active' and
            peserta.state == 'belum' and
            now >= paket.tanggal_mulai and
            now <= paket.tanggal_selesai
        )
        if paket.max_attempt > 0:
            can_start = can_start and peserta.attempt < paket.max_attempt
        values = {
            'peserta': peserta,
            'paket': paket,
            'now': now,
            'can_start': can_start,
            'format_datetime_tz': format_datetime_tz,
        }
        return request.render('al_ujian_online_school.portal_ujian_detail', values)

    @http.route('/my/ujian/<int:peserta_id>/start', type='http', auth='user', website=True)
    def portal_ujian_start(self, peserta_id, **kw):
        peserta = request.env['ujian.peserta'].sudo().browse(peserta_id)
        if not peserta.exists():
            return request.redirect('/my/ujian')
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if peserta.siswa_id.id != siswa.id:
            return request.redirect('/my/ujian')
        try:
            peserta.action_start_ujian()
            peserta.write({
                'ip_address': request.httprequest.remote_addr,
                'browser_info': request.httprequest.user_agent.string[:200] if request.httprequest.user_agent else '',
            })
        except Exception as e:
            return request.render('al_ujian_online_school.portal_ujian_error', {'error': str(e)})
        return request.redirect(f'/my/ujian/{peserta_id}/exam')

    @http.route('/my/ujian/<int:peserta_id>/exam', type='http', auth='user', website=True)
    def portal_ujian_exam(self, peserta_id, **kw):
        peserta = request.env['ujian.peserta'].sudo().browse(peserta_id)
        if not peserta.exists() or peserta.state != 'mengerjakan':
            return request.redirect('/my/ujian')
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if peserta.siswa_id.id != siswa.id:
            return request.redirect('/my/ujian')
        remaining = peserta.get_remaining_time()
        if remaining <= 0:
            peserta.action_submit_ujian()
            return request.redirect(f'/my/ujian/{peserta_id}/result')
        soal_order = json.loads(peserta.soal_order) if peserta.soal_order else []
        jawaban_list = peserta.jawaban_ids.sorted(lambda j: soal_order.index(j.soal_id.id) if j.soal_id.id in soal_order else 999)
        soal_idx = int(kw.get('soal_idx', 0))
        if soal_idx < 0:
            soal_idx = 0
        if soal_idx >= len(jawaban_list):
            soal_idx = len(jawaban_list) - 1
        current_jawaban = jawaban_list[soal_idx] if jawaban_list else None
        current_soal = current_jawaban.soal_id if current_jawaban else None
        pilihan_list = []
        if current_soal and current_soal.pilihan_ids:
            pilihan_list = list(current_soal.pilihan_ids.sorted('sequence'))
            if peserta.paket_id.acak_jawaban:
                import random
                random.seed(peserta.id + current_soal.id)
                random.shuffle(pilihan_list)
        peserta.write({'current_soal': soal_idx})
        values = {
            'peserta': peserta,
            'paket': peserta.paket_id,
            'jawaban_list': jawaban_list,
            'current_jawaban': current_jawaban,
            'current_soal': current_soal,
            'pilihan_list': pilihan_list,
            'soal_idx': soal_idx,
            'total_soal': len(jawaban_list),
            'remaining_time': remaining,
        }
        response = request.render('al_ujian_online_school.portal_ujian_exam', values)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @http.route('/my/ujian/<int:peserta_id>/save', type='json', auth='user')
    def portal_ujian_save(self, peserta_id, jawaban_id, answer_data, **kw):
        peserta = request.env['ujian.peserta'].sudo().browse(peserta_id)
        if not peserta.exists() or peserta.state != 'mengerjakan':
            return {'success': False, 'error': 'Invalid session'}
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if peserta.siswa_id.id != siswa.id:
            return {'success': False, 'error': 'Unauthorized'}
        jawaban = request.env['ujian.jawaban'].sudo().browse(jawaban_id)
        if not jawaban.exists() or jawaban.peserta_id.id != peserta.id:
            return {'success': False, 'error': 'Invalid jawaban'}
        try:
            jawaban.save_answer(answer_data)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/my/ujian/<int:peserta_id>/submit', type='http', auth='user', website=True, methods=['POST'])
    def portal_ujian_submit(self, peserta_id, **kw):
        peserta = request.env['ujian.peserta'].sudo().browse(peserta_id)
        if not peserta.exists() or peserta.state != 'mengerjakan':
            return request.redirect('/my/ujian')
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if peserta.siswa_id.id != siswa.id:
            return request.redirect('/my/ujian')
        peserta.action_submit_ujian()
        return request.redirect(f'/my/ujian/{peserta_id}/result')

    @http.route('/my/ujian/<int:peserta_id>/result', type='http', auth='user', website=True)
    def portal_ujian_result(self, peserta_id, **kw):
        peserta = request.env['ujian.peserta'].sudo().browse(peserta_id)
        if not peserta.exists():
            return request.redirect('/my/ujian')
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        if peserta.siswa_id.id != siswa.id:
            return request.redirect('/my/ujian')
        if peserta.state != 'selesai':
            return request.redirect(f'/my/ujian/{peserta_id}')
        paket = peserta.paket_id
        show_result = paket.tampilkan_hasil
        show_pembahasan = paket.tampilkan_pembahasan
        jawaban_list = peserta.jawaban_ids if show_pembahasan else []
        values = {
            'peserta': peserta,
            'paket': paket,
            'show_result': show_result,
            'show_pembahasan': show_pembahasan,
            'jawaban_list': jawaban_list,
            'format_datetime_tz': format_datetime_tz,
        }
        return request.render('al_ujian_online_school.portal_ujian_result', values)
