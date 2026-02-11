# Ujian Online School (CBT)

Modul Ujian Online/CBT (Computer Based Test) untuk Odoo 18.

## Fitur Utama

### Bank Soal
- Pilihan Ganda (PG)
- Pilihan Ganda Kompleks (Multi-answer)
- Benar/Salah
- Isian Singkat
- Essay
- Menjodohkan
- Import soal dari CSV
- Kategorisasi soal berdasarkan mata pelajaran
- Tingkat kesulitan (Mudah, Sedang, Sulit)
- Gambar pada soal dan pilihan jawaban
- Pembahasan untuk setiap soal

### Paket Ujian
- Berbagai jenis ujian (UH, PTS, PAS, PAT, Try Out, Remedial, Pengayaan)
- Pengaturan durasi fleksibel
- Jadwal mulai dan selesai
- Pengacakan urutan soal
- Pengacakan pilihan jawaban
- Batas maksimal percobaan
- KKM yang dapat disesuaikan
- Petunjuk ujian

### Portal Siswa (CBT)
- Tampilan modern dan responsif
- Timer countdown otomatis
- Auto-save jawaban
- Navigasi soal yang mudah
- Tandai soal ragu-ragu
- Hasil ujian langsung (opsional)
- Pembahasan jawaban (opsional)

### Koreksi & Analisis
- Koreksi otomatis untuk soal objektif (PG, Isian)
- Koreksi manual untuk Essay
- Analisis butir soal:
  - Tingkat kebenaran (correct rate)
  - Daya beda (discrimination index)
- Statistik per soal

### Laporan
- Laporan hasil ujian per siswa (PDF)
- Rekap nilai per paket ujian (PDF)
- Pivot dan grafik untuk analisis

## Dependencies
- sistem_sekolah_odoo18 (modul utama sistem sekolah)

## Instalasi
1. Copy folder `al_ujian_online_school` ke direktori addons Odoo
2. Update Apps List
3. Install modul "Ujian Online School (CBT)"

## Penggunaan

### 1. Membuat Kategori Soal
- Buka menu Ujian Online > Bank Soal > Kategori Soal
- Buat kategori berdasarkan mata pelajaran dan topik

### 2. Membuat Bank Soal
- Buka menu Ujian Online > Bank Soal > Semua Soal
- Klik "Create" untuk membuat soal baru
- Pilih tipe soal, tingkat kesulitan, dan kategori
- Isi pertanyaan dan pilihan jawaban (untuk PG)
- Tandai jawaban yang benar

### 3. Membuat Paket Ujian
- Buka menu Ujian Online > Ujian > Paket Ujian
- Klik "Create" untuk membuat paket baru
- Isi informasi ujian (judul, mata pelajaran, kelas, dll)
- Tambahkan soal dari bank soal ke daftar soal
- Atur pengaturan (pengacakan, tampilan hasil, dll)
- Klik "Siapkan" untuk menyiapkan ujian

### 4. Generate Peserta
- Dari paket ujian, klik "Generate Peserta"
- Pilih siswa yang akan mengikuti ujian
- Klik "Generate Peserta"

### 5. Aktivasi Ujian
- Klik "Aktifkan" untuk mengaktifkan ujian
- Siswa dapat mengakses ujian melalui portal

### 6. Monitoring & Koreksi
- Pantau peserta yang sedang mengerjakan
- Koreksi manual untuk soal essay
- Lihat hasil dan analisis

## Lisensi
LGPL-3
