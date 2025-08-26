<div align="center">

# 🚀 Instagram Content Uploader

### *Otomasi Posting Instagram yang Simpel dan Powerful*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![instagrapi](https://img.shields.io/badge/instagrapi-2.2.1-purple.svg)](https://github.com/subzeroid/instagrapi)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🎯 Set & Forget - Upload dan jadwalkan konten Instagram 24/7 tanpa intervensi manual!**

[🚀 Panduan Cepat](#-panduan-cepat) • [✨ Fitur Utama](#-fitur-utama) • [⚙️ Alur Kerja](#️-alur-kerja-aplikasi)

---

</div>

## ✨ **Fitur Utama**

<div align="center">

| 🎯 **Core Features** | 🔧 **Technical Features** | 🚀 **Advanced Features** |
|:---:|:---:|:---:|
| 📱 **Instagram Automation**<br/>Fokus pada satu platform | 🤖 **Private API**<br/>instagrapi Engine | ⏰ **Smart Scheduler**<br/>APScheduler Integration |
| 📅 **Auto Scheduling**<br/>Set & Forget | 🗄️ **Database Management**<br/>SQLite & MySQL Support | 🔐 **Session Management**<br/>Login aman & efisien |
| 🎨 **Web Dashboard**<br/>Modern UI/UX | 🌐 **Production Ready**<br/>Gunicorn + Web Server | 📊 **Analytics & Monitoring**<br/>Real-time Status |

</div>

---

## 🚀 **Panduan Cepat & Alur Kerja**

Bagian ini menjelaskan cara kerja aplikasi dari awal hingga akhir, termasuk cara deploy di server Anda sendiri (misalnya menggunakan aaPanel).

### ⚙️ **Alur Kerja Aplikasi**

Aplikasi ini menggunakan library `instagrapi` untuk berinteraksi dengan API internal (private) Instagram. Ini berbeda dari otomasi browser dan lebih stabil, tetapi memiliki alur kerja login yang spesifik.

**Penting: Proses Login Pertama Kali**

1.  **Login Awal:** Saat aplikasi pertama kali mencoba mengunggah sesuatu, `instagrapi` akan melakukan login menggunakan `INSTAGRAM_USERNAME` dan `INSTAGRAM_PASSWORD` dari file `.env` Anda.
2.  **Tantangan Keamanan (2FA):** Karena ini adalah login dari lokasi baru (server Anda), Instagram kemungkinan besar akan meminta verifikasi. `instagrapi` akan mendeteksi ini dan akan **berhenti dan menunggu input di konsol/terminal Anda**. Anda akan melihat prompt yang meminta kode 6 digit.
3.  **Masukkan Kode:** Periksa email yang terhubung dengan akun Instagram Anda, dapatkan kode 6 digit tersebut, dan masukkan ke dalam terminal tempat Anda menjalankan aplikasi.
4.  **Pembuatan Sesi:** Setelah kode dimasukkan dengan benar, login akan berhasil, dan `instagrapi` akan secara otomatis membuat file `session.json`. File ini berisi "kunci" sesi yang membuktikan bahwa perangkat Anda (server) sudah terverifikasi.
5.  **Login Berikutnya:** Untuk semua proses unggah di masa mendatang, aplikasi akan memuat `session.json` dan dapat login tanpa memerlukan nama pengguna, kata sandi, atau kode verifikasi lagi. Ini membuat prosesnya cepat dan aman.

> **CATATAN:** Pastikan Anda menjalankan aplikasi di terminal secara langsung (bukan sebagai service di latar belakang) untuk pertama kalinya agar Anda dapat melihat prompt untuk memasukkan kode 2FA.

### 📋 **Panduan Penggunaan Dasbor**

Setelah aplikasi berjalan, Anda dapat mengakses dasbor web (misalnya, di `http://your_domain:2009`).

1.  **Upload Konten:** Klik tombol "Upload Konten". Isi form, pilih file video/gambar, tulis caption, dan klik "Upload". Konten akan disimpan di database dan siap untuk diposting.
2.  **Posting Langsung:** Di daftar "Konten Terbaru", klik ikon "share" (panah) untuk langsung mempublikasikan konten tersebut ke Instagram.
3.  **Menjadwalkan Posting:** Anda dapat menjadwalkan postingan untuk waktu tertentu saat mengunggah, atau membuat jadwal harian dari menu "Jadwal Harian". Penjadwal akan secara otomatis memprosesnya pada waktu yang ditentukan.

### 🛠️ **Langkah-langkah Deployment di aaPanel**

Berikut adalah panduan langkah demi langkah untuk mendeploy aplikasi ini di server Anda menggunakan aaPanel.

**1. Persiapan di aaPanel:**
   - Buka aaPanel Anda.
   - Pergi ke menu **Website** -> **Add site**.
   - Buat website baru untuk domain atau subdomain Anda. Pastikan Anda juga membuat database MySQL jika Anda ingin menggunakannya (opsional, SQLite lebih mudah untuk memulai).

**2. Upload Kode:**
   - Pergi ke menu **Files**.
   - Navigasi ke direktori root website yang baru saja Anda buat (misalnya, `/www/wwwroot/domain.com`).
   - Hapus file default seperti `index.html`.
   - Upload semua file dari repositori ini ke direktori tersebut.

**3. Setup Lingkungan Python:**
   - Pergi ke menu **App Store**.
   - Cari dan install **Python Manager**.
   - Di dalam Python Manager, install versi Python yang sesuai (misalnya, 3.10 atau 3.11).
   - Kembali ke pengaturan **Website** Anda, pilih situs Anda, dan klik **Python Project**.
   - Klik **Add Python project**.
   - Pilih versi Python yang sudah Anda install.
   - **Framework:** Pilih `gunicorn`.
   - **Startup file/directory:** Masukkan `main.py`.
   - Klik **Confirm**. Ini akan membuat virtual environment untuk Anda.

**4. Install Dependencies:**
   - Setelah proyek Python dibuat, aaPanel akan memberikan path ke virtual environment Anda.
   - Buka **Terminal** di aaPanel.
   - Aktifkan virtual environment dengan perintah yang diberikan, contoh: `source /www/wwwroot/domain.com/pyenv/bin/activate`.
   - Jalankan perintah berikut untuk menginstal semua library yang diperlukan:
     ```bash
     pip install -r requirements.txt
     ```

**5. Konfigurasi `.env`:**
   - Di menu **Files**, masih di dalam direktori proyek Anda, salin `.env.example` menjadi file baru bernama `.env`.
   - Edit file `.env` tersebut:
     ```env
     # Gunakan SQLite untuk kemudahan
     DATABASE_URL=sqlite:///./daily_content.db

     # Masukkan kredensial Instagram Anda
     INSTAGRAM_USERNAME=username_ig_anda
     INSTAGRAM_PASSWORD=password_ig_anda

     # Atur port jika diperlukan (default 2009)
     PORT=2009
     ```

**6. Inisialisasi Database & Akun:**
   - Di **Terminal** (dengan virtual environment yang masih aktif), jalankan skrip setup:
     ```bash
     python setup.py
     ```
   - Skrip ini akan membuat tabel database dan menambahkan akun Instagram Anda ke dalamnya.

**7. Jalankan Aplikasi:**
   - Kembali ke pengaturan **Website** -> **Python Project**.
   - Klik **Start** atau **Restart** untuk memulai aplikasi Anda menggunakan Gunicorn.
   - Aplikasi Anda sekarang seharusnya sudah berjalan dan dapat diakses melalui domain Anda.
   - Jangan lupa untuk melakukan **proses login pertama kali** seperti yang dijelaskan di atas dengan menjalankan aplikasi secara manual di terminal untuk memasukkan kode 2FA.

---

## 🆘 **Troubleshooting**

*   **Error `Address already in use`:** Pastikan tidak ada proses lain yang menggunakan port yang sama. Anda bisa mengganti `PORT` di file `.env` Anda ke nomor lain (misalnya, 8008).
*   **Login Gagal Terus-menerus:** Hapus file `session.json` dan coba lagi proses login pertama kali. Pastikan kredensial di `.env` sudah benar.
*   **File Tidak Terupload:** Periksa izin folder `uploads/`. Pastikan user yang menjalankan aplikasi memiliki izin tulis (`chmod 755 uploads`).

---

**Happy Content Creating! 🎉**
