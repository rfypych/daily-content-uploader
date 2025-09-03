<div align="center">

[**English**](#) | [**Bahasa Indonesia**](./README_ID.md)

# 🚀 Instagram Content Uploader

### *Simple and Powerful Instagram Post Automation*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Framework](https://img.shields.io/badge/FastAPI-0.116+-green.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Scheduler](https://img.shields.io/badge/Scheduler-Custom-blueviolet.svg?style=for-the-badge)](./run_scheduler.py)
[![Uploader](https://img.shields.io/badge/Engine-instagrapi-purple.svg?style=for-the-badge)](https://github.com/subzeroid/instagrapi)

**🎯 Set & Forget - Upload and schedule Instagram content 24/7 without manual intervention!**

[🚀 Installation Guide](#-installation--setup-guide) • [✨ Key Features](#-key-features)

---

</div>

## ✨ **Key Features**

<div align="center">

| 🎯 **Core Features** | 🔧 **Technical Features** | 🚀 **Advanced Features** |
|:---:|:---:|:---:|
| 📱 **Instagram Automation**<br/>Focused on a single platform | 🤖 **Private API**<br/>instagrapi Engine | ⏰ **Custom Scheduler**<br/>Reliable Polling Service |
| 📅 **Auto Scheduling**<br/>One-time & Recurring | 🗄️ **Database Agnostic**<br/>SQLite & MySQL Support | 🔐 **Secure Login**<br/>Dashboard & Session Auth |
| 🎨 **Web Dashboard**<br/>Modern UI/UX | 🌐 **Production Ready**<br/>Gunicorn + Uvicorn | 📊 **Content Management**<br/>History & Status |

</div>

---

## 🚀 **Installation & Setup Guide**

Follow these steps to get the application running on your server.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/your-project.git
    cd daily-content-uploader
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:** Copy the example file to a new `.env` file.
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file and fill in all required credentials:
    - `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`
    - `WEB_USERNAME` and `WEB_PASSWORD` (for dashboard login)
    - `DATABASE_URL` (if not using default SQLite)
    - `TIMEZONE` (e.g., `Asia/Jakarta`)

4.  **Run the Interactive Setup Script:** Run `setup.py` from your server's terminal.
    ```bash
    python3 setup.py
    ```
    - This script will initialize the database and create the web user account.
    - It will then attempt to log in to Instagram.
    - **IMPORTANT:** Instagram may send a verification code (2FA) to your email. The script will pause and ask you to enter the 6-digit code in the terminal.
    - After a successful login, it will create `session.json`. This file helps maintain the login session to avoid future challenges.

### **Running the Application**

The application consists of two main components that must be run as persistent background services: the **Web Server** and the **Scheduler Service**.

1.  **Start the Web Server:**
    ```bash
    nohup gunicorn -c gunicorn_config.py main:app > gunicorn.log 2>&1 &
    ```
    This command starts the Gunicorn web server in the background and saves its logs to `gunicorn.log`.

2.  **Start the Scheduler Service:**
    ```bash
    nohup python3 run_scheduler.py > scheduler.log 2>&1 &
    ```
    This command starts the scheduler service in the background and saves its logs to `scheduler.log`.

You can now access your dashboard at `http://your_server_address:PORT` and log in with your `WEB_USERNAME` and `WEB_PASSWORD`.

---

## 🆘 **Troubleshooting**

*   **`challenge_required` or `LoginRequired` Error:** This is a security measure from Instagram. Stop the application, delete `session.json` (`rm session.json`), and re-run `python3 setup.py`. You may need to enter a new 2FA code. If this persists, the server's IP may be flagged by Instagram.
*   **Database Error (e.g., "Unknown column"):** This can happen after a code update. To fix this, you may need to reset your database. Run the setup script with the `--reset-db` flag on your server. **Warning: This will delete all your existing content and schedules.**
    ```bash
    python3 setup.py --reset-db
    ```

---

**Happy Content Creating! 🎉**
