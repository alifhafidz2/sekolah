{
    'name': 'Sistem Sekolah',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Sistem Manajemen Sekolah Lengkap',
    'description': """
        Sistem Manajemen Sekolah
        =========================
        Modul lengkap untuk manajemen sekolah yang mencakup:
        * Manajemen Data Siswa
        * Manajemen Data Guru
        * Manajemen Kelas
        * Mata Pelajaran
        * Jadwal Pelajaran
        * Absensi Siswa
        * Nilai & Rapor
        * Portal Siswa & Guru
        * Dashboard & Laporan
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'portal',
        'mail',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        'data/sequence_data.xml',

        'views/menu_views.xml',
        'views/siswa_views.xml',
        'views/guru_views.xml',
        'views/kelas_views.xml',
        'views/mata_pelajaran_views.xml',
        'views/jadwal_views.xml',
        'views/absensi_views.xml',
        'views/nilai_views.xml',
        'views/dashboard_views.xml',

        'views/portal_templates.xml',

        'wizard/absensi_massal_wizard_views.xml',
        'wizard/generate_jadwal_wizard_views.xml',

        'report/report_templates.xml',
        'report/rapor_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sistem_sekolah_odoo18/static/src/css/dashboard.css',
            'sistem_sekolah_odoo18/static/src/js/dashboard.js',
        ],
        'web.assets_frontend': [
            'sistem_sekolah_odoo18/static/src/css/portal.css',
        ],
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
