<div align="center">

[**English**](./README.md) | [**Bahasa Indonesia**](#)

# 🚀 Instagram Content Uploader

### *Otomasi Posting Instagram yang Simpel dan Powerful*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![instagrapi](https://img.shields.io/badge/instagrapi-2.2.1-purple.svg)](https://github.com/subzeroid/instagrapi)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🎯 Set & Forget - Upload dan jadwalkan konten Instagram 24/7 tanpa intervensi manual!**

[🚀 Panduan Instalasi](#-panduan-instalasi--setup) • [✨ Fitur Utama](#-fitur-utama)

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

## 🚀 **Panduan Instalasi & Setup**

Ikuti dua langkah utama ini untuk menjalankan aplikasi.

### **Langkah 1: Setup Awal (Hanya Perlu Dilakukan Sekali)**

Langkah ini bertujuan untuk menyiapkan konfigurasi, database, dan yang terpenting, melakukan login pertama kali ke Instagram untuk menyimpan sesi Anda.

1.  **Clone Repositori:**
    ```bash
    git clone https://github.com/rfypych/daily-content-uploader.git
    cd daily-content-uploader
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Konfigurasi Environment:** Salin file contoh menjadi file `.env` baru.
    ```bash
    cp .env.example .env
    ```
    Buka file `.env` tersebut dan isi kredensial Instagram Anda (`INSTAGRAM_USERNAME` dan `INSTAGRAM_PASSWORD`). Anda juga bisa mengganti `PORT` jika diperlukan.

4.  **Jalankan Skrip Setup Interaktif:** Jalankan skrip `setup.py` dari terminal Anda.
    ```bash
    python3 setup.py
    ```
    - Skrip ini akan membuat database (`daily_content.db`).
    - Kemudian, ia akan mencoba login ke Instagram.
    - **PENTING:** Instagram akan mengirimkan kode verifikasi (2FA) ke email Anda. Skrip akan berhenti dan meminta Anda memasukkan kode 6 digit tersebut di terminal.
    - Setelah kode dimasukkan dengan benar, skrip akan membuat file `session.json`. File ini adalah kunci Anda untuk login otomatis di masa mendatang.

Setelah `setup.py` selesai dan `session.json` berhasil dibuat, Anda siap untuk langkah berikutnya.

### **Langkah 2: Menjalankan Aplikasi**

Aplikasi ini terdiri dari dua komponen utama yang harus dijalankan secara terpisah di lingkungan production: **Server Web** dan **Penjadwal (Scheduler)**.

-   **Server Web:** Menangani antarmuka pengguna (dasbor) dan permintaan API.
-   **Penjadwal:** Berjalan di latar belakang untuk memproses unggahan yang dijadwalkan.

**Untuk Development:**
Anda bisa menjalankan kedua proses di dua terminal yang terpisah.
-   **Terminal 1 (Server Web):**
    ```bash
    python3 main.py
    ```
-   **Terminal 2 (Penjadwal):**
    ```bash
    python3 run_scheduler.py
    ```

**Untuk Production:**
Sangat penting untuk menjalankan keduanya sebagai service yang berjalan terus-menerus menggunakan process manager seperti `pm2` atau `supervisor`.
-   **Proses 1 (Server Web dengan Gunicorn):**
    ```bash
    gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:2009
    ```
-   **Proses 2 (Penjadwal):**
    ```bash
    python3 run_scheduler.py
    ```
Sekarang Anda dapat mengakses dasbor web di `http://alamat_server_anda:PORT` untuk mulai mengunggah dan menjadwalkan konten. Penjadwal akan secara otomatis mengambil tugas dari database.

---

### 📖 **Panduan Penggunaan Dasbor**

-   **Upload Konten:** Klik tombol "Upload Konten". Isi form, pilih file video/gambar, tulis caption, dan klik "Upload".
-   **Posting Langsung:** Di daftar "Konten Terbaru", klik ikon "share" (panah) untuk langsung mempublikasikan konten.
-   **Menjadwalkan Posting:** Atur jadwal saat mengunggah, atau buat jadwal harian dari menu "Jadwal Harian".

<details>
<summary><b>Panduan Deployment di aaPanel (Klik untuk membuka)</b></summary>

Berikut adalah panduan langkah demi langkah untuk mendeploy aplikasi ini di server Anda menggunakan aaPanel.

**1. Persiapan di aaPanel:**
   - Buka aaPanel Anda.
   - Pergi ke menu **Website** -> **Add site**.
   - Buat website baru untuk domain atau subdomain Anda.

**2. Upload Kode:**
   - Pergi ke menu **Files**.
   - Navigasi ke direktori root website yang baru saja Anda buat (misalnya, `/www/wwwroot/domain.com`).
   - Hapus file default seperti `index.html`.
   - Upload semua file dari repositori ini ke direktori tersebut.

**3. Setup Lingkungan Python:**
   - Pergi ke menu **App Store** dan install **Python Manager**.
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

**5. Konfigurasi dan Setup Awal:**
   - Masih di **Terminal** (dengan virtual environment aktif):
     - Buat file `.env`: `cp .env.example .env`
     - Edit file `.env` dengan editor nano: `nano .env`. Masukkan kredensial Instagram Anda, lalu simpan (Ctrl+X, Y, Enter).
     - Jalankan setup interaktif untuk login pertama kali:
       ```bash
       python3 setup.py
       ```
     - Ikuti prompt untuk memasukkan kode 2FA dari email Anda.

**6. Jalankan Aplikasi:**
   - Di manajer **Python Project** aaPanel untuk situs Anda, konfigurasikan perintah startup menjadi perintah Gunicorn:
     ```
     gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:2009
     ```
   - Klik **Start** atau **Restart**. Ini akan menjalankan server web.
   - Sekarang, buka lagi **Terminal** (pastikan virtual environment aktif: `source .../bin/activate`).
   - Jalankan penjadwal sebagai proses latar belakang yang persisten. Cara terbaik adalah menggunakan process manager seperti `pm2` atau `supervisor`. Jika tidak ada, Anda bisa menggunakan `nohup` untuk setup sederhana:
     ```bash
     nohup python3 run_scheduler.py &
     ```
   - Aplikasi Anda sekarang berjalan sepenuhnya.

</details>

---

## 🆘 **Troubleshooting**

*   **Error `Address already in use`:** Pastikan tidak ada proses lain yang menggunakan port yang sama. Anda bisa mengganti `PORT` di file `.env` Anda ke nomor lain (misalnya, 8008).
*   **Login Gagal Terus-menerus:** Hapus file `session.json` dan jalankan ulang `python3 setup.py` untuk melakukan proses login interaktif lagi.
*   **File Tidak Terupload:** Periksa izin folder `uploads/`. Pastikan user yang menjalankan aplikasi memiliki izin tulis (`chmod 755 uploads`).
*   **Error Database (Contoh: "Unknown column"):** Ini bisa terjadi jika Anda memperbarui kode aplikasi setelah database sudah dibuat. Untuk memperbaikinya, Anda perlu me-reset database Anda. Jalankan skrip setup dengan flag `--reset-db`. **Peringatan: Ini akan menghapus semua konten dan jadwal Anda yang ada.**
    ```bash
    python3 setup.py --reset-db
    ```

---

**Happy Content Creating! 🎉**
