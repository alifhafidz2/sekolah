# AL SPP School - Manajemen Pembayaran SPP

Modul Odoo 18 untuk mengelola pembayaran SPP (Sumbangan Pembinaan Pendidikan) di sekolah dan pondok pesantren.

## Fitur

- **Konfigurasi SPP**: Atur nominal SPP per kelas dan tahun ajaran
- **Generate Tagihan Otomatis**: Buat tagihan bulanan untuk semua siswa sekaligus
- **Multi Jenis Tagihan**: SPP bulanan, daftar ulang, kegiatan, seragam, buku
- **Pencatatan Pembayaran**: Tunai, transfer, QRIS, virtual account
- **Denda Keterlambatan**: Perhitungan denda otomatis
- **Portal Orang Tua**: Akses online untuk melihat tagihan dan pembayaran
- **Cetak Kwitansi**: Generate kwitansi PDF

## Cara Penggunaan

### 1. Instalasi

1. Pastikan addon `sistem_sekolah_odoo18` sudah terinstall
2. Copy folder `al_spp_school` ke direktori addons Odoo
3. Update Apps List di Odoo
4. Install addon "AL SPP School - Manajemen Pembayaran SPP"

### 2. Konfigurasi Awal

#### Setting Konfigurasi SPP

1. Buka menu **SPP > Konfigurasi > Konfigurasi SPP**
2. Klik tombol **Create** untuk membuat konfigurasi baru
3. Isi data:
   - **Tahun Ajaran**: Pilih tahun ajaran aktif
   - **Kelas**: Pilih kelas
   - **Nominal SPP**: Nominal SPP per bulan (contoh: 500.000)
   - **Daftar Ulang**: Biaya daftar ulang tahunan (opsional)
   - **Biaya Kegiatan**: Biaya kegiatan per semester (opsional)
   - **Biaya Seragam**: Biaya seragam (opsional)
   - **Biaya Buku**: Biaya buku (opsional)
4. Klik **Save**

Buat konfigurasi untuk setiap kombinasi kelas dan tahun ajaran.

### 3. Generate Tagihan SPP

#### Generate Tagihan Bulanan (SPP)

1. Buka **SPP > Konfigurasi > Konfigurasi SPP**
2. Pilih konfigurasi yang ingin di-generate tagihannya
3. Klik tombol **Generate Tagihan** di pojok kanan atas
4. Di popup wizard:
   - **Jenis Tagihan**: Pilih "SPP Bulanan"
   - **Bulan Mulai**: Bulan awal tagihan (default: Juli)
   - **Bulan Akhir**: Bulan akhir tagihan (default: Juni)
   - **Tahun**: Tahun tagihan
   - **Hari Jatuh Tempo**: Tanggal jatuh tempo setiap bulan (default: 10)
   - **Pilih Semua Siswa**: Centang untuk generate ke semua siswa aktif
5. Klik **Generate Tagihan**

Sistem akan otomatis membuat tagihan untuk setiap siswa di kelas tersebut untuk setiap bulan dalam rentang yang ditentukan.

#### Generate Tagihan Lainnya (Daftar Ulang, Kegiatan, dll)

1. Ikuti langkah yang sama seperti di atas
2. Pilih jenis tagihan yang sesuai (Daftar Ulang, Biaya Kegiatan, dll)
3. Tagihan akan dibuat sekali per siswa per tahun ajaran

### 4. Mengelola Tagihan

#### Melihat Daftar Tagihan

1. Buka menu **SPP > Tagihan > Semua Tagihan**
2. Gunakan filter untuk melihat:
   - Belum Lunas
   - Sebagian Dibayar
   - Lunas
   - Jatuh Tempo Lewat
3. Klik tagihan untuk melihat detail

#### Status Tagihan

- **Draft**: Tagihan baru dibuat, belum aktif
- **Belum Lunas**: Tagihan aktif, belum ada pembayaran
- **Sebagian**: Sudah ada pembayaran sebagian
- **Lunas**: Tagihan sudah dibayar penuh
- **Dibatalkan**: Tagihan dibatalkan

#### Melihat Tunggakan

1. Buka menu **SPP > Tagihan > Tunggakan**
2. Akan tampil semua tagihan yang sudah lewat jatuh tempo dan belum lunas

### 5. Mencatat Pembayaran

#### Dari Tagihan

1. Buka tagihan yang ingin dibayar
2. Klik tombol **Bayar**
3. Isi data pembayaran:
   - **Tanggal Bayar**: Tanggal pembayaran
   - **Nominal**: Jumlah yang dibayar
   - **Metode Bayar**: Tunai/Transfer/QRIS/VA
   - **Bank**: Pilih bank (untuk transfer/VA)
   - **No. Referensi**: Nomor bukti transfer (opsional)
   - **Bukti Pembayaran**: Upload foto bukti (opsional)
4. Klik **Save**
5. Klik **Konfirmasi** untuk mengkonfirmasi pembayaran

#### Pembayaran Langsung

1. Buka menu **SPP > Pembayaran > Semua Pembayaran**
2. Klik **Create**
3. Pilih tagihan yang ingin dibayar
4. Isi data pembayaran
5. Klik **Save** dan **Konfirmasi**

### 6. Melihat Riwayat Pembayaran

1. Buka menu **SPP > Pembayaran > Semua Pembayaran**
2. Filter berdasarkan:
   - Tanggal (Hari ini, Minggu ini, Bulan ini)
   - Metode pembayaran
   - Status

### 7. Cetak Kwitansi

1. Buka pembayaran yang sudah dikonfirmasi
2. Klik tombol **Cetak Kwitansi**
3. Kwitansi akan di-download dalam format PDF

### 8. Portal Orang Tua

#### Mengaktifkan Akses Portal

Pastikan siswa memiliki `wali_user_id` yang terhubung ke user portal orang tua.

#### Fitur Portal

Orang tua dapat mengakses:

1. **Daftar Tagihan** (`/my/spp`)
   - Melihat semua tagihan
   - Filter: Semua, Belum Lunas, Lunas
   - Melihat total tunggakan

2. **Detail Tagihan** (`/my/spp/tagihan/<id>`)
   - Informasi lengkap tagihan
   - Rincian biaya dan denda
   - Riwayat pembayaran

3. **Riwayat Pembayaran** (`/my/spp/pembayaran`)
   - Daftar semua pembayaran yang sudah dikonfirmasi
   - Total yang sudah dibayar

4. **Ringkasan Keuangan** (`/my/spp/ringkasan`)
   - Total tagihan keseluruhan
   - Total yang sudah dibayar
   - Sisa tunggakan
   - Rincian per jenis tagihan

## Hak Akses

### Petugas SPP (group_spp_user)
- Melihat konfigurasi SPP
- Mengelola tagihan (create, read, write)
- Mengelola pembayaran (create, read, write)
- Generate tagihan

### Manager SPP (group_spp_manager)
- Semua hak Petugas SPP
- Mengelola konfigurasi SPP
- Menghapus tagihan dan pembayaran

## Alur Kerja Umum

```
1. Setup awal (sekali per tahun ajaran):
   - Buat data Tahun Ajaran
   - Buat data Kelas
   - Buat data Siswa
   - Buat Konfigurasi SPP per kelas

2. Setiap awal tahun ajaran:
   - Generate tagihan SPP bulanan (Juli - Juni)
   - Generate tagihan daftar ulang (sekali)
   - Generate tagihan kegiatan (per semester)

3. Setiap hari:
   - Terima pembayaran dari orang tua
   - Catat pembayaran di sistem
   - Konfirmasi pembayaran
   - Cetak kwitansi

4. Monitoring:
   - Cek tunggakan secara berkala
   - Kirim pengingat ke orang tua (via WhatsApp jika ada)
```

## Tips

1. **Generate tagihan di awal**: Generate semua tagihan SPP di awal tahun ajaran agar orang tua bisa melihat jadwal pembayaran
2. **Gunakan filter**: Manfaatkan filter untuk memantau tunggakan dengan mudah
3. **Backup rutin**: Selalu backup database secara berkala
4. **Update status siswa**: Pastikan status siswa (aktif/tidak aktif) selalu update agar tagihan ter-generate dengan benar

## Troubleshooting

**Q: Tagihan tidak ter-generate untuk semua siswa?**
A: Pastikan semua siswa memiliki status "Active" dan terdaftar di kelas yang sesuai.

**Q: Denda tidak terhitung?**
A: Denda dihitung otomatis jika tagihan sudah melewati tanggal jatuh tempo. Pastikan tanggal server sudah benar.

**Q: Orang tua tidak bisa akses portal?**
A: Pastikan field `wali_user_id` di data siswa sudah terisi dengan user portal orang tua.
