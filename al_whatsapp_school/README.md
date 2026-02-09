# WhatsApp Notifikasi Absensi Sekolah

Addon Odoo 18 untuk mengirim notifikasi WhatsApp otomatis ketika siswa tercatat alfa.

## Fitur

- Kirim WhatsApp otomatis ke telepon ayah, ibu, dan wali
- Support provider: Fonnte, WaBlas, Woowa, Custom API
- Template pesan yang dapat dikustomisasi
- Log riwayat pengiriman
- Tombol kirim ulang

## Instalasi

1. Copy folder `al_whatsapp_school` ke direktori addons Odoo
2. Update Apps List di Odoo
3. Install addon "WhatsApp Notifikasi Absensi Sekolah"

## Konfigurasi

1. Buka menu **Sekolah > WhatsApp > Konfigurasi**
2. Pilih provider dan masukkan API Token
3. Atur template pesan
4. Aktifkan konfigurasi

## Variabel Template

- `{nama_siswa}` - Nama lengkap siswa
- `{kelas}` - Nama kelas
- `{nis}` - Nomor Induk Siswa
- `{tanggal}` - Tanggal absensi
- `{mapel}` - Mata pelajaran

## Dependensi

- sistem_sekolah_odoo18

## Lisensi

LGPL-3
