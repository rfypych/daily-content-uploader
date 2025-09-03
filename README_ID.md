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
| 📅 **Penjadwalan Otomatis**<br/>Sekali Jalan & Harian | 🗄️ **Database Agnostic**<br/>Dukungan SQLite & MySQL | 🔐 **Login Aman**<br/>Otentikasi Dasbor & Sesi |
| 🎨 **Dasbor Web**<br/>UI/UX Modern | 🌐 **Siap Produksi**<br/>Gunicorn + Uvicorn | 📊 **Manajemen Konten**<br/>Riwayat & Status |

</div>

---

## 🚀 **Panduan Instalasi & Setup**

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di server Anda.

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
    Buka file `.env` dan isi semua kredensial yang dibutuhkan:
    - `INSTAGRAM_USERNAME` dan `INSTAGRAM_PASSWORD`
    - `WEB_USERNAME` dan `WEB_PASSWORD` (untuk login dasbor)
    - `DATABASE_URL` (jika tidak menggunakan SQLite bawaan)
    - `TIMEZONE` (misal: `Asia/Jakarta`)

4.  **Jalankan Skrip Setup Interaktif:** Jalankan `setup.py` dari terminal server Anda.
    ```bash
    python3 setup.py
    ```
    - Skrip ini akan menginisialisasi database dan membuat akun pengguna web.
    - Kemudian, ia akan mencoba login ke Instagram.
    - **PENTING:** Instagram mungkin akan mengirimkan kode verifikasi (2FA) ke email Anda. Skrip akan berhenti dan meminta Anda memasukkan kode 6 digit di terminal.
    - Setelah login berhasil, skrip akan membuat `session.json`. File ini membantu menjaga sesi login untuk menghindari tantangan di masa depan.

### **Menjalankan Aplikasi**

Aplikasi ini terdiri dari dua komponen utama yang harus dijalankan sebagai servis latar belakang yang persisten: **Server Web** dan **Servis Penjadwal**.

1.  **Jalankan Server Web:**
    ```bash
    nohup gunicorn -c gunicorn_config.py main:app > gunicorn.log 2>&1 &
    ```
    Perintah ini memulai server web Gunicorn di latar belakang dan menyimpan semua log-nya ke `gunicorn.log`.

2.  **Jalankan Servis Penjadwal:**
    ```bash
    nohup python3 run_scheduler.py > scheduler.log 2>&1 &
    ```
    Perintah ini memulai servis penjadwal di latar belakang dan menyimpan semua log-nya ke `scheduler.log`.

Anda sekarang dapat mengakses dasbor Anda di `http://alamat_server_anda:PORT` dan login dengan `WEB_USERNAME` dan `WEB_PASSWORD` Anda.

---

## 🆘 **Troubleshooting**

*   **Error `challenge_required` atau `LoginRequired`:** Ini adalah langkah keamanan dari Instagram. Hentikan aplikasi, hapus `session.json` (`rm session.json`), dan jalankan ulang `python3 setup.py`. Anda mungkin perlu memasukkan kode 2FA yang baru. Jika ini terus terjadi, IP server Anda mungkin ditandai oleh Instagram.
*   **Error Database (Contoh: "Unknown column"):** Ini bisa terjadi setelah pembaruan kode. Untuk memperbaikinya, Anda mungkin perlu me-reset database Anda. Jalankan skrip setup dengan flag `--reset-db` di server Anda. **Peringatan: Ini akan menghapus semua konten dan jadwal Anda yang ada.**
    ```bash
    python3 setup.py --reset-db
    ```

---

**Selamat Membuat Konten! 🎉**
