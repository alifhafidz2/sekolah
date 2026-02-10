{
    'name': 'AL SPP School - Manajemen Pembayaran SPP',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Sistem Manajemen Pembayaran SPP Sekolah',
    'description': '''
        Modul Manajemen SPP untuk Sekolah/Pondok Pesantren
        ==================================================

        Fitur:
        - Konfigurasi nominal SPP per kelas dan tahun ajaran
        - Generate tagihan otomatis bulanan
        - Pencatatan pembayaran SPP
        - Laporan tunggakan dan pembayaran
        - Portal orang tua untuk melihat tagihan
        - Riwayat pembayaran lengkap
    ''',
    'author': 'AL School',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'sistem_sekolah_odoo18',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'wizard/generate_tagihan_wizard_views.xml',
        'views/spp_config_views.xml',
        'views/spp_tagihan_views.xml',
        'views/spp_pembayaran_views.xml',
        'views/menu_views.xml',
        'views/portal_templates.xml',
        'report/report_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'al_spp_school/static/src/css/portal.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
