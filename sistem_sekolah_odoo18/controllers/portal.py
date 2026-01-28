from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class SekolahPortal(CustomerPortal):

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

        return request.render('sistem_sekolah_odoo18.portal_siswa_jadwal', {
            'siswa': siswa,
            'jadwal_by_hari': jadwal_by_hari,
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

        return request.render('sistem_sekolah_odoo18.portal_guru_jadwal', {
            'guru': guru,
            'jadwal_by_hari': jadwal_by_hari,
            'hari_list': hari_list,
            'page_name': 'guru_jadwal',
        })
