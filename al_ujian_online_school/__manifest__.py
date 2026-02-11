{
    'name': 'Ujian Online School (CBT)',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Sistem Ujian Online/CBT dengan Bank Soal dan Analisis Butir Soal',
    'description': '''
        Modul Ujian Online untuk Sekolah
        ================================
        Fitur:
        - Bank Soal (Pilihan Ganda, Essay, Isian Singkat, Benar/Salah)
        - Paket Ujian dengan pengaturan durasi dan jadwal
        - Computer Based Test (CBT) untuk siswa
        - Koreksi otomatis untuk soal objektif
        - Analisis butir soal (tingkat kesulitan, daya beda)
        - Portal siswa untuk mengerjakan ujian
        - Laporan hasil ujian
    ''',
    'author': 'Sistem Sekolah',
    'website': 'https://www.yourschool.com',
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
        'views/kategori_soal_views.xml',
        'views/bank_soal_views.xml',
        'views/paket_ujian_views.xml',
        'views/peserta_ujian_views.xml',
        'views/analisis_views.xml',
        'views/menu_views.xml',
        'views/portal_templates.xml',
        'wizard/generate_peserta_wizard_views.xml',
        'wizard/import_soal_wizard_views.xml',
        'report/report_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'al_ujian_online_school/static/src/css/portal.css',
            'al_ujian_online_school/static/src/js/ujian.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
