<div align="center">

[**English**](./README.md) | [**Bahasa Indonesia**](#)

# 🚀 Instagram Content Uploader

### *Otomasi Posting Instagram yang Simpel dan Powerful*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Framework](https://img.shields.io/badge/FastAPI-0.116+-green.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Scheduler](https://img.shields.io/badge/Scheduler-Custom-blueviolet.svg?style=for-the-badge)](./run_scheduler.py)
[![Uploader](https://img.shields.io/badge/Engine-instagrapi-purple.svg?style=for-the-badge)](https://github.com/subzeroid/instagrapi)

**🎯 Set & Forget - Upload dan jadwalkan konten Instagram 24/7 tanpa intervensi manual!**

[🚀 Panduan Instalasi](#-panduan-instalasi--setup) • [✨ Fitur Utama](#-fitur-utama)

---

</div>

## ✨ **Fitur Utama**

<div align="center">

| 🎯 **Fitur Inti** | 🔧 **Fitur Teknis** | 🚀 **Fitur Lanjutan** |
|:---:|:---:|:---:|
| 📱 **Otomasi Instagram**<br/>Fokus pada satu platform | 🤖 **Private API**<br/>Mesin instagrapi | ⏰ **Penjadwal Cerdas**<br/>Servis Polling Kustom |
| 📅 **Penjadwalan Otomatis**<br/>Sekali Jalan & Harian | 🗄️ **Database Agnostic**<br/>Dukungan SQLite & MySQL | 🔐 **Manajemen Sesi**<br/>Login aman & efisien |
| 🎨 **Dasbor Web**<br/>UI/UX Modern | 🌐 **Siap Produksi**<br/>Gunicorn + Uvicorn | 📊 **Manajemen Konten**<br/>Riwayat & Status |

</div>

---

## 🚀 **Panduan Instalasi & Setup**

Ikuti dua langkah utama ini untuk menjalankan aplikasi.

### **Langkah 1: Setup Awal (Hanya Perlu Dilakukan Sekali)**

Langkah ini bertujuan untuk menyiapkan konfigurasi, database, dan yang terpenting, melakukan login pertama kali ke Instagram untuk menyimpan sesi Anda.

1.  **Clone Repositori:**
    ```bash
    git clone https://github.com/your-repo/your-project.git
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
    Buka file `.env` tersebut dan isi kredensial Instagram Anda (`INSTAGRAM_USERNAME` dan `INSTAGRAM_PASSWORD`). Anda juga bisa mengganti `PORT` dan `TIMEZONE` (misal: `Asia/Jakarta`).

4.  **Jalankan Skrip Setup Interaktif:** Jalankan skrip `setup.py` dari terminal Anda.
    ```bash
    python3 setup.py
    ```
    - Skrip ini akan membuat database.
    - Kemudian, ia akan mencoba login ke Instagram.
    - **PENTING:** Instagram akan mengirimkan kode verifikasi (2FA) ke email Anda. Skrip akan berhenti dan meminta Anda memasukkan kode 6 digit tersebut di terminal.
    - Setelah kode dimasukkan dengan benar, skrip akan membuat file `session.json`. File ini adalah kunci Anda untuk login otomatis di masa mendatang.

Setelah `setup.py` selesai dan `session.json` berhasil dibuat, Anda siap untuk langkah berikutnya.

### **Langkah 2: Menjalankan Aplikasi**

Aplikasi ini terdiri dari dua komponen utama yang harus dijalankan secara terpisah: **Server Web** dan **Servis Penjadwal**.

-   **Server Web (`main.py`):** Menangani antarmuka pengguna (dasbor) dan permintaan API untuk membuat konten dan "niat" jadwal.
-   **Servis Penjadwal (`run_scheduler.py`):** Servis yang dibuat khusus yang berjalan di latar belakang. Ia secara berkala memeriksa database untuk "niat" jadwal baru, dan ketika pekerjaan jatuh tempo, ia menjalankan unggahan.

#### **Untuk Produksi**
Sangat penting untuk menjalankan keduanya sebagai servis latar belakang yang persisten. Menggunakan `nohup` dengan pengalihan log adalah cara yang kuat untuk mencapai ini.

1.  **Jalankan Server Web:**
    ```bash
    nohup gunicorn -c gunicorn_config.py main:app > gunicorn.log 2>&1 &
    ```
    Perintah ini memulai server web Gunicorn di latar belakang dan menyimpan semua outputnya ke `gunicorn.log`.

2.  **Jalankan Servis Penjadwal:**
    ```bash
    nohup python3 run_scheduler.py > scheduler.log 2>&1 &
    ```
    Perintah ini memulai servis penjadwal di latar belakang dan menyimpan semua outputnya ke `scheduler.log`.

Anda sekarang dapat mengakses dasbor web di `http://alamat_server_anda:PORT`.

---

### 📖 **Panduan Penggunaan Dasbor**

-   **Upload Konten:** Klik tombol "New Upload". Isi form, pilih file video/gambar, tulis caption, dan klik "Upload".
-   **Posting Langsung:** Di daftar "Content History", klik ikon "share" (panah) untuk langsung mempublikasikan konten.
-   **Menjadwalkan Posting:** Gunakan tombol "Schedule for a specific time" (ikon kalender) untuk posting sekali jalan, atau buat jadwal berulang dari menu "Daily Schedule".

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

**Selamat Membuat Konten! 🎉**
