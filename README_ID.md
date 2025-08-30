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

Aplikasi ini menggunakan alur kerja yang kuat untuk menghindari pemicuan sistem keamanan Instagram. Setup dibagi menjadi dua bagian: setup satu kali di **komputer lokal** Anda, dan deployment di **server** Anda.

### **Bagian 1: Pembuatan Sesi (di Komputer Lokal Anda)**

Langkah terpenting adalah membuat file `session.json` di mesin yang tepercaya (komputer pribadi Anda) untuk menghindari tantangan login di server.

1.  **Clone Repositori secara Lokal:**
    ```bash
    git clone https://github.com/your-repo/your-project.git
    cd daily-content-uploader
    ```

2.  **Install Dependencies secara Lokal:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Konfigurasi Environment Lokal:** Buat file `.env` dari contoh.
    ```bash
    cp .env.example .env
    ```
    Buka file `.env` dan isi `INSTAGRAM_USERNAME` dan `INSTAGRAM_PASSWORD` Anda.

4.  **Jalankan Setup Interaktif secara Lokal:** Jalankan skrip `setup.py`.
    ```bash
    python3 setup.py
    ```
    - Skrip akan memandu Anda melalui proses login Instagram.
    - **Masukkan kode 2FA** yang dikirim ke email Anda saat diminta.
    - Setelah berhasil, sebuah file `session.json` akan dibuat di direktori proyek Anda. File ini sangat penting.

### **Bagian 2: Deployment Server**

Sekarang, Anda akan men-deploy kode aplikasi dan file sesi yang telah dibuat ke server Anda.

1.  **Upload File Proyek:** Upload semua file proyek (kecuali `session.json` untuk saat ini) ke server Anda (misalnya, di `/www/wwwroot/domain.anda.com`).

2.  **Konfigurasi Environment Server:**
    - Buat file `.env` di server (`cp .env.example .env`).
    - Isi `DATABASE_URL` Anda.
    - Atur `WEB_USERNAME` dan `WEB_PASSWORD` untuk login dasbor Anda.
    - Atur `TIMEZONE` Anda (misalnya, `Asia/Jakarta`).
    - **Biarkan `INSTAGRAM_USERNAME` dan `INSTAGRAM_PASSWORD` kosong di server.** Ini penting untuk keamanan.

3.  **Upload File Sesi:** Upload file `session.json` yang Anda buat di Bagian 1 secara aman ke direktori proyek di server Anda.

4.  **Inisialisasi Database Server:**
    - Masuk ke server Anda melalui SSH dan navigasikan ke direktori proyek.
    - Jalankan skrip setup **tanpa bagian login** untuk menginisialisasi database dan membuat pengguna web.
    ```bash
    python3 setup.py
    ```
    *(Karena INSTAGRAM_USERNAME kosong di .env server, skrip akan melewatkan bagian login interaktif).*

5.  **Jalankan Aplikasi:**
    Jalankan server web dan penjadwal sebagai servis latar belakang yang persisten.
    -   **Server Web:**
        ```bash
        nohup gunicorn -c gunicorn_config.py main:app > gunicorn.log 2>&1 &
        ```
    -   **Servis Penjadwal:**
        ```bash
        nohup python3 run_scheduler.py > scheduler.log 2>&1 &
        ```

Anda sekarang dapat mengakses dasbor Anda di `http://alamat_server_anda:PORT` dan login dengan `WEB_USERNAME` dan `WEB_PASSWORD` Anda.

---

## 🆘 **Troubleshooting**

*   **Error `Session is invalid`:** File `session.json` Anda telah kedaluwarsa atau tidak valid. Anda harus mengulangi **Bagian 1** di komputer lokal Anda untuk membuat `session.json` yang baru, lalu upload ulang hanya file tersebut ke server Anda.
*   **Error Database (Contoh: "Unknown column"):** Ini bisa terjadi setelah pembaruan kode. Untuk memperbaikinya, Anda mungkin perlu me-reset database Anda. Jalankan skrip setup dengan flag `--reset-db` di server Anda. **Peringatan: Ini akan menghapus semua konten dan jadwal Anda yang ada.**
    ```bash
    python3 setup.py --reset-db
    ```

---

**Selamat Membuat Konten! 🎉**
