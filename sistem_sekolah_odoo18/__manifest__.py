{
    'name': 'Sistem Sekolah Indonesia',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Sistem Manajemen Sekolah Lengkap untuk SD, SMP, SMA, SMK',
    'description': """
Sistem Manajemen Sekolah Indonesia - Odoo 18
=============================================

Solusi lengkap dan terintegrasi untuk manajemen sekolah modern di Indonesia.
Dirancang khusus untuk kebutuhan pendidikan di Indonesia dengan fitur-fitur
yang sesuai dengan kurikulum dan standar nasional.

FITUR UTAMA
-----------

**Master Data**
* Manajemen Data Siswa lengkap dengan biodata, foto, dan data orang tua
* Database Guru dengan spesialisasi dan riwayat mengajar
* Pengelolaan Kelas dengan wali kelas dan kapasitas
* Mata Pelajaran dengan KKM (Kriteria Ketuntasan Minimal)
* Tahun Ajaran dan Semester

**Akademik**
* Jadwal Pelajaran dengan deteksi konflik otomatis
* Generate jadwal otomatis dengan wizard
* Tampilan kalender untuk visualisasi jadwal
* Absensi siswa individual dan massal
* Statistik kehadiran real-time

**Penilaian**
* Komponen nilai: Tugas, UTS, UAS, Praktik
* Bobot nilai yang dapat dikustomisasi
* Perhitungan otomatis nilai akhir
* Predikat dan status kelulusan berdasarkan KKM
* Generate Rapor PDF otomatis

**Portal Web**
* Portal akses untuk siswa melihat nilai dan absensi
* Portal akses untuk guru melihat jadwal mengajar
* Tampilan responsif untuk mobile

**Dashboard & Laporan**
* Dashboard analytics real-time
* Statistik kehadiran dan nilai
* Laporan per kelas dan siswa
* Export data ke PDF

**Keamanan**
* Multi-level user access (Admin, User, Portal)
* Role-based permission
* Audit trail

KEUNGGULAN
----------
* Interface modern dan user-friendly
* Validasi data otomatis
* Deteksi konflik jadwal
* Perhitungan statistik real-time
* 100% kompatibel dengan Odoo 18
* Support bahasa Indonesia
* Dokumentasi lengkap

COCOK UNTUK
-----------
* Sekolah Dasar (SD)
* Sekolah Menengah Pertama (SMP)
* Sekolah Menengah Atas (SMA)
* Sekolah Menengah Kejuruan (SMK)
* Madrasah (MI, MTs, MA)
* Pondok Pesantren

SUPPORT & GARANSI
-----------------
* Dokumentasi lengkap
* Video tutorial
* Support via WhatsApp/Email
* Update gratis selama 1 tahun
* Garansi 30 hari uang kembali
    """,
    'author': 'Al Tech Solutions',
    'website': 'https://github.com/altechsolutions',
    'license': 'LGPL-3',
    'price': 99.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': [
        'base',
        'web',
        'website',
        'portal',
        'mail',
    ],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        'data/sequence_data.xml',

        'views/menu_views.xml',
        'views/tahun_ajaran_views.xml',
        'views/siswa_views.xml',
        'views/guru_views.xml',
        'views/kelas_views.xml',
        'views/mata_pelajaran_views.xml',
        'views/jadwal_views.xml',
        'views/absensi_views.xml',
        'views/nilai_views.xml',
        'views/dashboard_views.xml',

        'views/portal_templates.xml',
        'views/portal_wali_templates.xml',

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
