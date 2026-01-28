# Sistem Sekolah - Odoo 18

Modul Odoo 18 untuk Sistem Manajemen Sekolah Lengkap

## Fitur

### Master Data
- **Siswa**: Manajemen data lengkap siswa dengan foto, biodata, data akademik, dan orang tua
- **Guru**: Database guru dengan spesialisasi, pendidikan, dan status kepegawaian
- **Kelas**: Pengelompokan siswa dengan wali kelas dan kapasitas
- **Mata Pelajaran**: Master data mapel dengan KKM dan kategori

### Akademik
- **Jadwal Pelajaran**:
  - Penjadwalan dengan tampilan kalender
  - Deteksi konflik otomatis (guru & kelas)
  - Generate jadwal otomatis
  - Multi tahun ajaran

- **Absensi**:
  - Input individual atau massal
  - Statistik kehadiran real-time
  - Riwayat absensi lengkap
  - Filter per kelas/siswa

- **Nilai**:
  - Komponen nilai: Tugas, UTS, UAS, Praktik
  - Bobot nilai customizable
  - Perhitungan otomatis
  - Predikat dan status kelulusan
  - KKM per mata pelajaran

### Portal Web
Portal akses untuk siswa dan guru:

**Siswa dapat melihat:**
- Profil lengkap
- Daftar nilai dengan status kelulusan
- Riwayat absensi dengan statistik
- Jadwal pelajaran kelas

**Guru dapat melihat:**
- Profil kepegawaian
- Jadwal mengajar
- Data kelas yang diwalikan

### Laporan
- Rapor siswa (PDF)
- Statistik kehadiran
- Rekap nilai per kelas
- Dashboard analytics

## Instalasi

### Requirements
- Odoo 18.0
- Python 3.10+
- PostgreSQL 12+

### Cara Install

1. Copy folder `sistem_sekolah_odoo18` ke direktori addons Odoo
2. Update apps list di Odoo
3. Cari "Sistem Sekolah" di Apps
4. Klik Install

Atau via command line:
```bash
./odoo-bin -u sistem_sekolah_odoo18 -d nama_database
```

## Konfigurasi

### Setup Awal

1. **Tahun Ajaran**
   - Buat tahun ajaran aktif di: Konfigurasi > Tahun Ajaran
   - Set status "Aktif"

2. **Master Data**
   - Input mata pelajaran dengan KKM
   - Input data guru
   - Buat kelas dengan wali kelas

3. **Siswa**
   - Input data siswa
   - Assign ke kelas

4. **Jadwal**
   - Manual: Buat jadwal satu per satu
   - Otomatis: Gunakan wizard "Generate Jadwal"

5. **Portal Setup** (Optional)
   - Buat user portal di Settings > Users
   - Link user ke siswa/guru via field "Portal User"
   - Siswa/guru bisa login di `/web/login`

## Penggunaan

### Input Absensi Massal

1. Menu: Akademik > Input Absensi Massal
2. Pilih kelas dan jadwal
3. Ubah status siswa jika perlu
4. Klik "Buat Absensi"

### Input Nilai

1. Menu: Akademik > Nilai > Create
2. Pilih siswa dan mata pelajaran
3. Input nilai komponen (Tugas, UTS, UAS, Praktik)
4. Nilai akhir dihitung otomatis
5. Save

### Generate Rapor

1. Buka data siswa
2. Klik Print > Rapor Siswa
3. PDF akan di-generate otomatis

## Struktur Database

### Model Utama

- `sekolah.siswa` - Data siswa
- `sekolah.guru` - Data guru
- `sekolah.kelas` - Data kelas
- `sekolah.mata_pelajaran` - Mata pelajaran
- `sekolah.jadwal` - Jadwal pelajaran
- `sekolah.absensi` - Absensi siswa
- `sekolah.nilai` - Nilai siswa
- `sekolah.tahun_ajaran` - Tahun ajaran

### Security Groups

- **User**: Akses penuh CRUD semua data
- **Administrator**: Akses penuh + konfigurasi sistem
- **Portal**: Read-only untuk data pribadi

## Validasi & Business Rules

### Siswa
- NIS harus unik
- Umur dihitung otomatis dari tanggal lahir
- Statistik absensi real-time

### Guru
- NIP harus unik
- Bisa mengampu multiple mata pelajaran
- Bisa jadi wali kelas

### Kelas
- Kapasitas maksimum siswa
- Warning jika kelas penuh
- Auto-count jumlah siswa

### Jadwal
- Jam selesai > jam mulai
- Tidak boleh bentrok untuk guru yang sama
- Tidak boleh bentrok untuk kelas yang sama

### Absensi
- Tidak boleh duplikat (siswa + jadwal + tanggal)
- Auto-generate kode absensi

### Nilai
- Nilai 0-100
- Total bobot harus 100%
- Tidak boleh duplikat (siswa + mapel + semester)
- Status kelulusan otomatis berdasarkan KKM

## Workflow Operasional

### Awal Tahun Ajaran
1. Buat tahun ajaran baru
2. Set sebagai aktif
3. Setup kelas baru
4. Assign wali kelas
5. Input/mutasi siswa ke kelas baru
6. Generate jadwal pelajaran

### Harian
1. Guru input absensi (via wizard massal)
2. Monitor kehadiran siswa

### Per Semester
1. Input nilai per komponen
2. Sistem hitung nilai akhir otomatis
3. Generate rapor di akhir semester
4. Evaluasi dan remedial jika perlu

### Akhir Tahun Ajaran
1. Export data nilai
2. Set tahun ajaran "Selesai"
3. Update status siswa (naik kelas/lulus)

## Customization

### Menambah Komponen Nilai
Edit file `models/nilai.py`:
- Tambah field nilai baru
- Update `_compute_nilai_akhir`
- Edit form view

### Mengubah Bobot Default
Edit `models/nilai.py` di field:
- `bobot_tugas`
- `bobot_uts`
- `bobot_uas`
- `bobot_praktik`

### Custom Report
Duplicate template di `report/rapor_template.xml` dan customize sesuai kebutuhan.

## Troubleshooting

### Jadwal Bentrok
- Periksa jadwal guru di hari yang sama
- Periksa jadwal kelas di jam yang sama
- Gunakan view calendar untuk visualisasi

### Portal Tidak Bisa Akses
- Pastikan user sudah di-assign ke siswa/guru
- Cek user memiliki grup "Portal"
- Clear browser cache

### Nilai Tidak Tersimpan
- Pastikan total bobot = 100%
- Cek nilai dalam range 0-100
- Pastikan tidak ada duplikat data

## Support & Development

Untuk bug report, feature request, atau kontribusi, silakan hubungi tim development.

## License

LGPL-3

## Credits

Developed for Odoo 18 Education Management System
