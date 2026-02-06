from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from werkzeug.utils import redirect


class SekolahPortal(CustomerPortal):

    def _float_to_time_string(self, float_time):
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def _build_jadwal_with_breaks(self, jadwal_by_hari):
        result = {}
        for hari, jadwal_list in jadwal_by_hari.items():
            items = []
            for i, jadwal in enumerate(jadwal_list):
                if i > 0:
                    prev = jadwal_list[i - 1]
                    gap = jadwal.jam_mulai - prev.jam_selesai
                    if gap >= 0.08:
                        items.append({
                            'type': 'istirahat',
                            'display_time': f"{self._float_to_time_string(prev.jam_selesai)} - {self._float_to_time_string(jadwal.jam_mulai)}",
                        })
                items.append({
                    'type': 'jadwal',
                    'record': jadwal,
                })
            result[hari] = items
        return result

    @http.route(['/my', '/my/home'], type='http', auth='user', website=True)
    def home(self, **kw):
        return redirect('/my/sekolah')

    @http.route(['/my/sekolah', '/sekolah/home'], type='http', auth='user', website=True)
    def portal_sekolah_home(self, **kw):
        user = request.env.user

        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)

        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)

        total_siswa = request.env['sekolah.siswa'].sudo().search_count([('status', '=', 'aktif')])
        total_guru = request.env['sekolah.guru'].sudo().search_count([('status', '=', 'aktif')])
        total_kelas = request.env['sekolah.kelas'].sudo().search_count([])
        total_mapel = request.env['sekolah.mata_pelajaran'].sudo().search_count([])

        return request.render('sistem_sekolah_odoo18.portal_sekolah_home', {
            'user': user,
            'siswa': siswa,
            'guru': guru,
            'total_siswa': total_siswa,
            'total_guru': total_guru,
            'total_kelas': total_kelas,
            'total_mapel': total_mapel,
            'page_name': 'sekolah_home',
        })

    @http.route(['/my/sekolah/tentang-kami'], type='http', auth='user', website=True)
    def portal_tentang_kami(self, **kw):
        return request.render('sistem_sekolah_odoo18.portal_tentang_kami', {
            'page_name': 'tentang_kami',
        })

    @http.route(['/my/sekolah/program-kurikulum'], type='http', auth='user', website=True)
    def portal_program_kurikulum(self, **kw):
        return request.render('sistem_sekolah_odoo18.portal_program_kurikulum', {
            'page_name': 'program_kurikulum',
        })

    @http.route(['/my/sekolah/fasilitas'], type='http', auth='user', website=True)
    def portal_fasilitas(self, **kw):
        return request.render('sistem_sekolah_odoo18.portal_fasilitas', {
            'page_name': 'fasilitas',
        })

    @http.route(['/my/sekolah/kehidupan-santri'], type='http', auth='user', website=True)
    def portal_kehidupan_santri(self, **kw):
        return request.render('sistem_sekolah_odoo18.portal_kehidupan_santri', {
            'page_name': 'kehidupan_santri',
        })

    @http.route(['/my/sekolah/kontak'], type='http', auth='user', website=True)
    def portal_kontak(self, **kw):
        return request.render('sistem_sekolah_odoo18.portal_kontak', {
            'page_name': 'kontak',
        })

    @http.route(['/my/siswa'], type='http', auth='user', website=True)
    def portal_my_siswa(self, **kw):
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not siswa:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data siswa tidak ditemukan'
            })

        return request.render('sistem_sekolah_odoo18.portal_siswa_profile', {
            'siswa': siswa,
            'page_name': 'siswa_profile',
        })

    @http.route(['/my/siswa/nilai'], type='http', auth='user', website=True)
    def portal_my_nilai(self, **kw):
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not siswa:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data siswa tidak ditemukan'
            })

        nilai_list = request.env['sekolah.nilai'].sudo().search([
            ('siswa_id', '=', siswa.id)
        ], order='tahun_ajaran_id desc, semester desc')

        return request.render('sistem_sekolah_odoo18.portal_siswa_nilai', {
            'siswa': siswa,
            'nilai_list': nilai_list,
            'page_name': 'nilai',
        })

    @http.route(['/my/siswa/absensi'], type='http', auth='user', website=True)
    def portal_my_absensi(self, **kw):
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not siswa:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data siswa tidak ditemukan'
            })

        absensi_list = request.env['sekolah.absensi'].sudo().search([
            ('siswa_id', '=', siswa.id)
        ], order='tanggal desc', limit=100)

        return request.render('sistem_sekolah_odoo18.portal_siswa_absensi', {
            'siswa': siswa,
            'absensi_list': absensi_list,
            'page_name': 'absensi',
        })

    @http.route(['/my/siswa/jadwal'], type='http', auth='user', website=True)
    def portal_my_jadwal(self, **kw):
        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not siswa or not siswa.kelas_id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data siswa atau kelas tidak ditemukan'
            })

        jadwal_list = request.env['sekolah.jadwal'].sudo().search([
            ('kelas_id', '=', siswa.kelas_id.id)
        ], order='hari, jam_mulai')

        hari_list = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu']
        jadwal_by_hari = {hari: [] for hari in hari_list}

        for jadwal in jadwal_list:
            jadwal_by_hari[jadwal.hari].append(jadwal)

        jadwal_with_breaks = self._build_jadwal_with_breaks(jadwal_by_hari)

        return request.render('sistem_sekolah_odoo18.portal_siswa_jadwal', {
            'siswa': siswa,
            'jadwal_by_hari': jadwal_by_hari,
            'jadwal_with_breaks': jadwal_with_breaks,
            'hari_list': hari_list,
            'page_name': 'jadwal',
        })

    @http.route(['/my/guru'], type='http', auth='user', website=True)
    def portal_my_guru(self, **kw):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data guru tidak ditemukan'
            })

        return request.render('sistem_sekolah_odoo18.portal_guru_profile', {
            'guru': guru,
            'page_name': 'guru_profile',
        })

    @http.route(['/my/guru/jadwal'], type='http', auth='user', website=True)
    def portal_guru_jadwal(self, **kw):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data guru tidak ditemukan'
            })

        jadwal_list = request.env['sekolah.jadwal'].sudo().search([
            ('guru_id', '=', guru.id)
        ], order='hari, jam_mulai')

        hari_list = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu']
        jadwal_by_hari = {hari: [] for hari in hari_list}

        for jadwal in jadwal_list:
            jadwal_by_hari[jadwal.hari].append(jadwal)

        jadwal_with_breaks = self._build_jadwal_with_breaks(jadwal_by_hari)

        return request.render('sistem_sekolah_odoo18.portal_guru_jadwal', {
            'guru': guru,
            'jadwal_by_hari': jadwal_by_hari,
            'jadwal_with_breaks': jadwal_with_breaks,
            'hari_list': hari_list,
            'page_name': 'guru_jadwal',
        })
