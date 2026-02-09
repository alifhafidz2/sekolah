{
    'name': 'WhatsApp Notifikasi Sekolah',
    'version': '18.0.1.0.0',
    'category': 'Education',
    'summary': 'Kirim notifikasi WhatsApp otomatis ke orang tua siswa',
    'description': """
WhatsApp Notifikasi Sekolah - Odoo 18
=====================================

Addon integrasi WhatsApp untuk modul Sistem Sekolah Indonesia.
Kirim notifikasi otomatis ke orang tua/wali ketika siswa tercatat alfa.

FITUR UTAMA
-----------

**Multi-Provider Support**
* Fonnte - Provider populer Indonesia
* WaBlas - Alternatif terpercaya
* Woowa - Pilihan ekonomis
* WAHA (WhatsApp HTTP API) - Self-hosted solution
* Custom API - Integrasi provider lain

**Notifikasi Otomatis**
* Kirim ke telepon Ayah
* Kirim ke telepon Ibu
* Kirim ke telepon Wali
* Trigger otomatis saat absensi = Alfa

**Template Pesan Dinamis**
* Variabel: {nama_siswa}, {kelas}, {nis}, {tanggal}, {mapel}
* Customizable sesuai kebutuhan
* Preview pesan sebelum kirim

**Monitoring & Log**
* Riwayat pengiriman lengkap
* Status: Berhasil / Gagal
* Tombol kirim ulang
* Filter dan pencarian

KEUNGGULAN
----------
* Integrasi seamless dengan Sistem Sekolah
* Setup mudah dalam 5 menit
* Hemat biaya komunikasi
* Meningkatkan keterlibatan orang tua
* Log lengkap untuk audit

CARA KERJA
----------
1. Install addon setelah Sistem Sekolah terinstall
2. Konfigurasi provider WhatsApp di menu Settings
3. Masukkan API Token dari provider
4. Atur template pesan
5. Aktifkan konfigurasi
6. Ketika siswa dicatat alfa, notifikasi otomatis terkirim

SUPPORT
-------
* Dokumentasi lengkap
* Panduan konfigurasi per provider
* Support via WhatsApp/Email
    """,
    'author': 'Al Tech Solutions',
    'website': 'https://github.com/altechsolutions',
    'license': 'LGPL-3',
    'price': 49.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
    'depends': ['sistem_sekolah_odoo18'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_log_views.xml',
        'views/whatsapp_config_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
