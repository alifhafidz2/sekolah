from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class SppPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'tagihan_count' in counters:
            user = request.env.user
            siswa = request.env['sekolah.siswa'].sudo().search([
                '|',
                ('user_id', '=', user.id),
                ('wali_user_id', '=', user.id),
            ], limit=1)
            if siswa:
                tagihan_count = request.env['al.spp.tagihan'].sudo().search_count([
                    ('siswa_id', '=', siswa.id),
                    ('state', 'in', ['open', 'partial']),
                ])
                values['tagihan_count'] = tagihan_count
            else:
                values['tagihan_count'] = 0
        return values

    def _get_siswa_for_user(self):
        user = request.env.user
        return request.env['sekolah.siswa'].sudo().search([
            '|',
            ('user_id', '=', user.id),
            ('wali_user_id', '=', user.id),
        ], limit=1)

    @http.route(['/my/spp', '/my/spp/page/<int:page>'], type='http', auth='user', website=True)
    def portal_spp_list(self, page=1, sortby=None, filterby=None, **kw):
        siswa = self._get_siswa_for_user()
        if not siswa:
            return request.render('al_spp_school.portal_spp_no_access', {})

        Tagihan = request.env['al.spp.tagihan'].sudo()

        domain = [('siswa_id', '=', siswa.id)]

        sortings = {
            'date': {'label': 'Terbaru', 'order': 'tahun desc, bulan desc'},
            'name': {'label': 'Nomor', 'order': 'name'},
            'state': {'label': 'Status', 'order': 'state'},
        }
        if not sortby:
            sortby = 'date'

        filters = {
            'all': {'label': 'Semua', 'domain': []},
            'open': {'label': 'Belum Lunas', 'domain': [('state', 'in', ['open', 'partial'])]},
            'paid': {'label': 'Lunas', 'domain': [('state', '=', 'paid')]},
        }
        if not filterby:
            filterby = 'all'

        domain += filters[filterby]['domain']

        tagihan_count = Tagihan.search_count(domain)
        pager = portal_pager(
            url='/my/spp',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=tagihan_count,
            page=page,
            step=10,
        )

        tagihan_list = Tagihan.search(
            domain,
            order=sortings[sortby]['order'],
            limit=10,
            offset=pager['offset'],
        )

        total_tunggakan = sum(t.sisa_tagihan for t in Tagihan.search([
            ('siswa_id', '=', siswa.id),
            ('state', 'in', ['open', 'partial']),
        ]))

        values = {
            'siswa': siswa,
            'tagihan_list': tagihan_list,
            'pager': pager,
            'sortby': sortby,
            'sortings': sortings,
            'filterby': filterby,
            'filters': filters,
            'total_tunggakan': total_tunggakan,
            'page_name': 'spp',
        }
        return request.render('al_spp_school.portal_spp_list', values)

    @http.route('/my/spp/tagihan/<int:tagihan_id>', type='http', auth='user', website=True)
    def portal_spp_detail(self, tagihan_id, **kw):
        siswa = self._get_siswa_for_user()
        if not siswa:
            return request.render('al_spp_school.portal_spp_no_access', {})

        tagihan = request.env['al.spp.tagihan'].sudo().browse(tagihan_id)
        if not tagihan.exists() or tagihan.siswa_id.id != siswa.id:
            return request.redirect('/my/spp')

        values = {
            'siswa': siswa,
            'tagihan': tagihan,
            'page_name': 'spp_detail',
        }
        return request.render('al_spp_school.portal_spp_detail', values)

    @http.route('/my/spp/pembayaran', type='http', auth='user', website=True)
    def portal_spp_pembayaran(self, **kw):
        siswa = self._get_siswa_for_user()
        if not siswa:
            return request.render('al_spp_school.portal_spp_no_access', {})

        Pembayaran = request.env['al.spp.pembayaran'].sudo()
        pembayaran_list = Pembayaran.search([
            ('siswa_id', '=', siswa.id),
            ('state', '=', 'confirmed'),
        ], order='tanggal_bayar desc', limit=50)

        total_dibayar = sum(p.nominal for p in pembayaran_list)

        values = {
            'siswa': siswa,
            'pembayaran_list': pembayaran_list,
            'total_dibayar': total_dibayar,
            'page_name': 'spp_pembayaran',
        }
        return request.render('al_spp_school.portal_spp_pembayaran', values)

    @http.route('/my/spp/ringkasan', type='http', auth='user', website=True)
    def portal_spp_ringkasan(self, **kw):
        siswa = self._get_siswa_for_user()
        if not siswa:
            return request.render('al_spp_school.portal_spp_no_access', {})

        Tagihan = request.env['al.spp.tagihan'].sudo()
        Pembayaran = request.env['al.spp.pembayaran'].sudo()

        tagihan_all = Tagihan.search([('siswa_id', '=', siswa.id)])
        pembayaran_all = Pembayaran.search([
            ('siswa_id', '=', siswa.id),
            ('state', '=', 'confirmed'),
        ])

        total_tagihan = sum(t.total_tagihan for t in tagihan_all if t.state != 'cancel')
        total_terbayar = sum(p.nominal for p in pembayaran_all)
        total_tunggakan = sum(t.sisa_tagihan for t in tagihan_all if t.state in ['open', 'partial'])

        tagihan_by_jenis = {}
        for t in tagihan_all:
            if t.state != 'cancel':
                jenis = dict(t._fields['jenis_tagihan'].selection).get(t.jenis_tagihan)
                if jenis not in tagihan_by_jenis:
                    tagihan_by_jenis[jenis] = {'tagihan': 0, 'terbayar': 0}
                tagihan_by_jenis[jenis]['tagihan'] += t.total_tagihan
                tagihan_by_jenis[jenis]['terbayar'] += t.nominal_terbayar

        values = {
            'siswa': siswa,
            'total_tagihan': total_tagihan,
            'total_terbayar': total_terbayar,
            'total_tunggakan': total_tunggakan,
            'tagihan_by_jenis': tagihan_by_jenis,
            'page_name': 'spp_ringkasan',
        }
        return request.render('al_spp_school.portal_spp_ringkasan', values)
