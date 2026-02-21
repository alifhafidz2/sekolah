from odoo import http, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from werkzeug.utils import redirect
from datetime import datetime, date


class SekolahPublic(http.Controller):

    @http.route(['/'], type='http', auth='public', website=True, csrf=False)
    def landing_page(self, **kw):
        total_siswa = request.env['sekolah.siswa'].sudo().search_count([('status', '=', 'aktif')])
        total_guru = request.env['sekolah.guru'].sudo().search_count([('status', '=', 'aktif')])
        total_kelas = request.env['sekolah.kelas'].sudo().search_count([])
        total_mapel = request.env['sekolah.mata_pelajaran'].sudo().search_count([])

        return request.render('sistem_sekolah_odoo18.public_landing_page', {
            'total_siswa': total_siswa,
            'total_guru': total_guru,
            'total_kelas': total_kelas,
            'total_mapel': total_mapel,
        })

    @http.route(['/portal'], type='http', auth='user', website=True)
    def portal_redirect(self, **kw):
        return redirect('/my/sekolah')


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
                if jadwal.break_before_start and jadwal.break_before_end:
                    items.append({
                        'type': 'istirahat',
                        'display_time': f"{self._float_to_time_string(jadwal.break_before_start)} - {self._float_to_time_string(jadwal.break_before_end)}",
                    })
                elif i > 0:
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

        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)

        if guru:
            return redirect('/my/guru')

        siswa = request.env['sekolah.siswa'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)

        if siswa:
            return redirect('/my/siswa')

        anak_list = request.env['sekolah.siswa'].sudo().search([
            ('wali_user_id', '=', user.id)
        ])

        if anak_list:
            return redirect('/my/wali')

        return request.render('sistem_sekolah_odoo18.portal_no_access', {
            'message': 'Anda tidak terdaftar sebagai guru, siswa, atau wali. Silakan hubungi administrator.',
        })

    @http.route(['/my/wali'], type='http', auth='user', website=True)
    def portal_wali_home(self, **kw):
        user = request.env.user
        anak_list = request.env['sekolah.siswa'].sudo().search([
            ('wali_user_id', '=', user.id),
            ('status', '=', 'aktif')
        ])

        if not anak_list:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Tidak ada data anak yang terdaftar untuk akun ini'
            })

        summary_data = []
        for anak in anak_list:
            absensi_stats = {
                'total': anak.total_absensi,
                'hadir': anak.total_hadir,
                'izin': anak.total_izin,
                'sakit': anak.total_sakit,
                'alfa': anak.total_alfa,
                'persentase': anak.persentase_kehadiran,
            }

            tagihan_belum_lunas = []
            total_tunggakan = 0
            if 'al.spp.tagihan' in request.env:
                tagihan_belum_lunas = request.env['al.spp.tagihan'].sudo().search([
                    ('siswa_id', '=', anak.id),
                    ('state', 'in', ['open', 'partial'])
                ], order='tanggal_jatuh_tempo asc', limit=3)
                total_tunggakan = sum(t.sisa_tagihan for t in tagihan_belum_lunas)

            summary_data.append({
                'anak': anak,
                'absensi': absensi_stats,
                'rata_nilai': anak.rata_rata_nilai,
                'tagihan_belum_lunas': tagihan_belum_lunas,
                'total_tunggakan': total_tunggakan,
            })

        return request.render('sistem_sekolah_odoo18.portal_wali_home', {
            'anak_list': anak_list,
            'summary_data': summary_data,
            'page_name': 'wali_home',
        })

    @http.route(['/my/wali/anak/<int:siswa_id>'], type='http', auth='user', website=True)
    def portal_wali_anak_detail(self, siswa_id, **kw):
        user = request.env.user
        siswa = request.env['sekolah.siswa'].sudo().browse(siswa_id)

        if not siswa.exists() or siswa.wali_user_id.id != user.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data tidak ditemukan atau Anda tidak memiliki akses'
            })

        return request.render('sistem_sekolah_odoo18.portal_wali_anak_detail', {
            'siswa': siswa,
            'page_name': 'wali_anak_detail',
        })

    @http.route(['/my/wali/absensi/<int:siswa_id>'], type='http', auth='user', website=True)
    def portal_wali_absensi(self, siswa_id, **kw):
        user = request.env.user
        siswa = request.env['sekolah.siswa'].sudo().browse(siswa_id)

        if not siswa.exists() or siswa.wali_user_id.id != user.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data tidak ditemukan atau Anda tidak memiliki akses'
            })

        absensi_list = request.env['sekolah.absensi'].sudo().search([
            ('siswa_id', '=', siswa.id)
        ], order='tanggal desc', limit=100)

        stats = {
            'total': siswa.total_absensi,
            'hadir': siswa.total_hadir,
            'izin': siswa.total_izin,
            'sakit': siswa.total_sakit,
            'alfa': siswa.total_alfa,
            'persentase': siswa.persentase_kehadiran,
        }

        return request.render('sistem_sekolah_odoo18.portal_wali_absensi', {
            'siswa': siswa,
            'absensi_list': absensi_list,
            'stats': stats,
            'page_name': 'wali_absensi',
        })

    @http.route(['/my/wali/nilai/<int:siswa_id>'], type='http', auth='user', website=True)
    def portal_wali_nilai(self, siswa_id, **kw):
        user = request.env.user
        siswa = request.env['sekolah.siswa'].sudo().browse(siswa_id)

        if not siswa.exists() or siswa.wali_user_id.id != user.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data tidak ditemukan atau Anda tidak memiliki akses'
            })

        nilai_list = request.env['sekolah.nilai'].sudo().search([
            ('siswa_id', '=', siswa.id)
        ], order='tahun_ajaran_id desc, semester desc')

        return request.render('sistem_sekolah_odoo18.portal_wali_nilai', {
            'siswa': siswa,
            'nilai_list': nilai_list,
            'rata_rata': siswa.rata_rata_nilai,
            'page_name': 'wali_nilai',
        })

    @http.route(['/my/wali/spp/<int:siswa_id>'], type='http', auth='user', website=True)
    def portal_wali_spp(self, siswa_id, filter_state='all', **kw):
        user = request.env.user
        siswa = request.env['sekolah.siswa'].sudo().browse(siswa_id)

        if not siswa.exists() or siswa.wali_user_id.id != user.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data tidak ditemukan atau Anda tidak memiliki akses'
            })

        if 'al.spp.tagihan' not in request.env:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Modul SPP belum diinstall'
            })

        domain = [('siswa_id', '=', siswa.id)]
        if filter_state == 'unpaid':
            domain.append(('state', 'in', ['open', 'partial']))
        elif filter_state == 'paid':
            domain.append(('state', '=', 'paid'))

        tagihan_list = request.env['al.spp.tagihan'].sudo().search(
            domain, order='tahun desc, bulan desc'
        )

        total_tagihan = sum(t.total_tagihan for t in tagihan_list if t.state != 'cancel')
        total_terbayar = sum(t.nominal_terbayar for t in tagihan_list if t.state != 'cancel')
        total_tunggakan = sum(t.sisa_tagihan for t in tagihan_list if t.state in ['open', 'partial'])

        return request.render('sistem_sekolah_odoo18.portal_wali_spp', {
            'siswa': siswa,
            'tagihan_list': tagihan_list,
            'filter_state': filter_state,
            'total_tagihan': total_tagihan,
            'total_terbayar': total_terbayar,
            'total_tunggakan': total_tunggakan,
            'page_name': 'wali_spp',
        })

    @http.route(['/my/wali/spp/<int:siswa_id>/detail/<int:tagihan_id>'], type='http', auth='user', website=True)
    def portal_wali_spp_detail(self, siswa_id, tagihan_id, **kw):
        user = request.env.user
        siswa = request.env['sekolah.siswa'].sudo().browse(siswa_id)

        if not siswa.exists() or siswa.wali_user_id.id != user.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data tidak ditemukan atau Anda tidak memiliki akses'
            })

        if 'al.spp.tagihan' not in request.env:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Modul SPP belum diinstall'
            })

        tagihan = request.env['al.spp.tagihan'].sudo().browse(tagihan_id)
        if not tagihan.exists() or tagihan.siswa_id.id != siswa.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Tagihan tidak ditemukan'
            })

        return request.render('sistem_sekolah_odoo18.portal_wali_spp_detail', {
            'siswa': siswa,
            'tagihan': tagihan,
            'page_name': 'wali_spp_detail',
        })

    @http.route(['/my/wali/jadwal/<int:siswa_id>'], type='http', auth='user', website=True)
    def portal_wali_jadwal(self, siswa_id, **kw):
        user = request.env.user
        siswa = request.env['sekolah.siswa'].sudo().browse(siswa_id)

        if not siswa.exists() or siswa.wali_user_id.id != user.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data tidak ditemukan atau Anda tidak memiliki akses'
            })

        if not siswa.kelas_id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Siswa belum memiliki kelas'
            })

        jadwal_list = request.env['sekolah.jadwal'].sudo().search([
            ('kelas_id', '=', siswa.kelas_id.id)
        ], order='hari, jam_mulai')

        hari_list = ['senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu']
        jadwal_by_hari = {hari: [] for hari in hari_list}

        for jadwal in jadwal_list:
            jadwal_by_hari[jadwal.hari].append(jadwal)

        return request.render('sistem_sekolah_odoo18.portal_wali_jadwal', {
            'siswa': siswa,
            'jadwal_by_hari': jadwal_by_hari,
            'hari_list': hari_list,
            'page_name': 'wali_jadwal',
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

    @http.route(['/my/guru/absensi'], type='http', auth='user', website=True)
    def portal_guru_absensi(self, **kw):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data guru tidak ditemukan'
            })

        jadwal_list = request.env['sekolah.jadwal'].sudo().search([
            ('guru_id', '=', guru.id)
        ], order='kelas_id, hari, jam_mulai')

        kelas_dict = {}
        for jadwal in jadwal_list:
            if jadwal.kelas_id.id not in kelas_dict:
                kelas_dict[jadwal.kelas_id.id] = {
                    'kelas': jadwal.kelas_id,
                    'jadwal_count': 0,
                    'siswa_count': len(jadwal.kelas_id.siswa_ids),
                }
            kelas_dict[jadwal.kelas_id.id]['jadwal_count'] += 1

        kelas_list = list(kelas_dict.values())

        return request.render('sistem_sekolah_odoo18.portal_guru_absensi_home', {
            'guru': guru,
            'kelas_list': kelas_list,
            'page_name': 'guru_absensi',
        })

    @http.route(['/my/guru/absensi/kelas/<int:kelas_id>'], type='http', auth='user', website=True)
    def portal_guru_absensi_kelas(self, kelas_id, **kw):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data guru tidak ditemukan'
            })

        kelas = request.env['sekolah.kelas'].sudo().browse(kelas_id)
        if not kelas.exists():
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Kelas tidak ditemukan'
            })

        jadwal_list = request.env['sekolah.jadwal'].sudo().search([
            ('guru_id', '=', guru.id),
            ('kelas_id', '=', kelas_id)
        ], order='hari, jam_mulai')

        today = date.today()
        hari_map = {
            0: 'senin', 1: 'selasa', 2: 'rabu',
            3: 'kamis', 4: 'jumat', 5: 'sabtu', 6: 'minggu'
        }
        hari_ini = hari_map.get(today.weekday(), 'senin')

        jadwal_hari_ini = [j for j in jadwal_list if j.hari == hari_ini]

        return request.render('sistem_sekolah_odoo18.portal_guru_absensi_kelas', {
            'guru': guru,
            'kelas': kelas,
            'jadwal_list': jadwal_list,
            'jadwal_hari_ini': jadwal_hari_ini,
            'hari_ini': hari_ini,
            'tanggal_hari_ini': today,
            'page_name': 'guru_absensi_kelas',
        })

    @http.route(['/my/guru/absensi/input/<int:jadwal_id>'], type='http', auth='user', website=True)
    def portal_guru_absensi_input(self, jadwal_id, tanggal=None, **kw):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data guru tidak ditemukan'
            })

        jadwal = request.env['sekolah.jadwal'].sudo().browse(jadwal_id)
        if not jadwal.exists() or jadwal.guru_id.id != guru.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Jadwal tidak ditemukan atau Anda tidak memiliki akses'
            })

        if tanggal:
            try:
                selected_date = datetime.strptime(tanggal, '%Y-%m-%d').date()
            except ValueError:
                selected_date = date.today()
        else:
            selected_date = date.today()

        siswa_list = request.env['sekolah.siswa'].sudo().search([
            ('kelas_id', '=', jadwal.kelas_id.id),
            ('status', '=', 'aktif')
        ], order='name')

        existing_absensi = request.env['sekolah.absensi'].sudo().search([
            ('jadwal_id', '=', jadwal_id),
            ('tanggal', '=', selected_date)
        ])
        absensi_dict = {ab.siswa_id.id: ab for ab in existing_absensi}

        siswa_absensi = []
        for siswa in siswa_list:
            absensi = absensi_dict.get(siswa.id)
            siswa_absensi.append({
                'siswa': siswa,
                'absensi': absensi,
                'status': absensi.status if absensi else 'hadir',
                'keterangan': absensi.keterangan if absensi else '',
            })

        stats = {
            'total': len(siswa_list),
            'hadir': sum(1 for sa in siswa_absensi if sa['status'] == 'hadir'),
            'izin': sum(1 for sa in siswa_absensi if sa['status'] == 'izin'),
            'sakit': sum(1 for sa in siswa_absensi if sa['status'] == 'sakit'),
            'alfa': sum(1 for sa in siswa_absensi if sa['status'] == 'alfa'),
        }

        return request.render('sistem_sekolah_odoo18.portal_guru_absensi_input', {
            'guru': guru,
            'jadwal': jadwal,
            'siswa_absensi': siswa_absensi,
            'selected_date': selected_date,
            'stats': stats,
            'has_existing': len(existing_absensi) > 0,
            'page_name': 'guru_absensi_input',
        })

    @http.route(['/my/guru/absensi/submit'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_guru_absensi_submit(self, **post):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return redirect('/my/guru/absensi')

        jadwal_id = int(post.get('jadwal_id', 0))
        tanggal_str = post.get('tanggal', '')

        jadwal = request.env['sekolah.jadwal'].sudo().browse(jadwal_id)
        if not jadwal.exists() or jadwal.guru_id.id != guru.id:
            return redirect('/my/guru/absensi')

        try:
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
        except ValueError:
            tanggal = date.today()

        absensi_obj = request.env['sekolah.absensi'].sudo()

        siswa_list = request.env['sekolah.siswa'].sudo().search([
            ('kelas_id', '=', jadwal.kelas_id.id),
            ('status', '=', 'aktif')
        ])

        tahun_ajaran = request.env['sekolah.tahun_ajaran'].sudo().search([
            ('is_active', '=', True)
        ], limit=1)

        for siswa in siswa_list:
            status = post.get(f'status_{siswa.id}', 'hadir')
            keterangan = post.get(f'keterangan_{siswa.id}', '')

            existing = absensi_obj.search([
                ('siswa_id', '=', siswa.id),
                ('jadwal_id', '=', jadwal_id),
                ('tanggal', '=', tanggal)
            ], limit=1)

            if existing:
                existing.write({
                    'status': status,
                    'keterangan': keterangan,
                })
            else:
                absensi_obj.create({
                    'siswa_id': siswa.id,
                    'jadwal_id': jadwal_id,
                    'tanggal': tanggal,
                    'status': status,
                    'keterangan': keterangan,
                    'tahun_ajaran_id': tahun_ajaran.id if tahun_ajaran else False,
                })

        return redirect(f'/my/guru/absensi/input/{jadwal_id}?tanggal={tanggal_str}&success=1')

    @http.route(['/my/guru/absensi/riwayat/<int:jadwal_id>'], type='http', auth='user', website=True)
    def portal_guru_absensi_riwayat(self, jadwal_id, **kw):
        guru = request.env['sekolah.guru'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)

        if not guru:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Data guru tidak ditemukan'
            })

        jadwal = request.env['sekolah.jadwal'].sudo().browse(jadwal_id)
        if not jadwal.exists() or jadwal.guru_id.id != guru.id:
            return request.render('sistem_sekolah_odoo18.portal_no_data', {
                'message': 'Jadwal tidak ditemukan atau Anda tidak memiliki akses'
            })

        absensi_list = request.env['sekolah.absensi'].sudo().search([
            ('jadwal_id', '=', jadwal_id)
        ], order='tanggal desc, siswa_id')

        dates_dict = {}
        for ab in absensi_list:
            date_key = ab.tanggal
            if date_key not in dates_dict:
                dates_dict[date_key] = {
                    'tanggal': date_key,
                    'hadir': 0,
                    'izin': 0,
                    'sakit': 0,
                    'alfa': 0,
                    'total': 0,
                }
            dates_dict[date_key][ab.status] += 1
            dates_dict[date_key]['total'] += 1

        riwayat_list = sorted(dates_dict.values(), key=lambda x: x['tanggal'], reverse=True)

        return request.render('sistem_sekolah_odoo18.portal_guru_absensi_riwayat', {
            'guru': guru,
            'jadwal': jadwal,
            'riwayat_list': riwayat_list,
            'page_name': 'guru_absensi_riwayat',
        })
