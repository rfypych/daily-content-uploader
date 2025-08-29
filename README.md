<div align="center">

[**English**](#) | [**Bahasa Indonesia**](./README_ID.md)

# 🚀 Instagram Content Uploader

### *Simple and Powerful Instagram Post Automation*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![instagrapi](https://img.shields.io/badge/instagrapi-2.2.1-purple.svg)](https://github.com/subzeroid/instagrapi)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🎯 Set & Forget - Upload and schedule Instagram content 24/7 without manual intervention!**

[🚀 Installation Guide](#-installation--setup-guide) • [✨ Key Features](#-key-features)

---

</div>

## ✨ **Key Features**

<div align="center">

| 🎯 **Core Features** | 🔧 **Technical Features** | 🚀 **Advanced Features** |
|:---:|:---:|:---:|
| 📱 **Instagram Automation**<br/>Focused on a single platform | 🤖 **Private API**<br/>instagrapi Engine | ⏰ **Smart Scheduler**<br/>APScheduler Integration |
| 📅 **Auto Scheduling**<br/>Set & Forget | 🗄️ **Database Management**<br/>SQLite & MySQL Support | 🔐 **Session Management**<br/>Secure & efficient login |
| 🎨 **Web Dashboard**<br/>Modern UI/UX | 🌐 **Production Ready**<br/>Gunicorn + Web Server | 📊 **Analytics & Monitoring**<br/>Real-time Status |

</div>

---

## 🚀 **Installation & Setup Guide**

Follow these two main steps to get the application running.

### **Step 1: Initial Setup (Only Needs to be Done Once)**

This step prepares the configuration, database, and most importantly, performs the initial login to Instagram to save your session.

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
    Open the `.env` file and fill in your Instagram credentials (`INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`). You can also change the `PORT` and `TIMEZONE` if needed.

4.  **Run the Interactive Setup Script:** Run the `setup.py` script from your terminal.
    ```bash
    python3 setup.py
    ```
    - This script will create the database (`daily_content.db`).
    - It will then attempt to log in to Instagram.
    - **IMPORTANT:** Instagram will send a verification code (2FA) to your email. The script will pause and ask you to enter the 6-digit code in the terminal.
    - After entering the code correctly, the script will create a `session.json` file. This file is your key for automatic logins in the future.

Once `setup.py` is complete and `session.json` is successfully created, you are ready for the next step.

### **Step 2: Running the Application**

The application consists of two main components that must be run separately in a production environment: the **Web Server** and the **Scheduler**.

-   **Web Server:** Handles the user interface (dashboard) and API requests.
-   **Scheduler:** Runs in the background to process scheduled uploads.

**For Development:**
You can run both processes in two separate terminals.
-   **Terminal 1 (Web Server):**
    ```bash
    python3 main.py
    ```
-   **Terminal 2 (Scheduler):**
    ```bash
    python3 run_scheduler.py
    ```

**For Production:**
It is crucial to run both as persistent services using a process manager like `pm2` or `supervisor`. For a simple setup, you can use `nohup`.
-   **Process 1 (Web Server with Gunicorn):**
    ```bash
    nohup gunicorn -c gunicorn_config.py main:app &
    ```
-   **Process 2 (Scheduler):**
    ```bash
    nohup python3 run_scheduler.py &
    ```
You can now access the web dashboard at `http://your_server_address:PORT` to start uploading and scheduling content. The scheduler will automatically pick up tasks from the database.

---

### 📖 **Dashboard Usage Guide**

-   **Upload Content:** Click the "New Upload" button. Fill out the form, select a video/image file, write a caption, and click "Upload".
-   **Publish Immediately:** In the "Content History" list, click the "share" icon (arrow) to publish content instantly.
-   **Schedule a Post:** Use the "Schedule for a specific time" button (calendar icon) for one-time posts, or create a recurring schedule from the "Daily Schedule" menu.

---

## 🆘 **Troubleshooting**

*   **Error `Address already in use`:** Make sure no other process is using the same port. You can change the `PORT` in your `.env` file to another number (e.g., 8008).
*   **Persistent Login Failures:** Delete the `session.json` file and re-run `python3 setup.py` to perform the interactive login process again.
*   **File Not Uploading:** Check the permissions of the `uploads/` folder. Ensure the user running the application has write permissions (`chmod 755 uploads`).
*   **Database Error (e.g., "Unknown column"):** This can happen if you update the application code after the database has already been created. To fix this, you need to reset your database. Run the setup script with the `--reset-db` flag. **Warning: This will delete all your existing content and schedules.**
    ```bash
    python3 setup.py --reset-db
    ```

---

**Happy Content Creating! 🎉**
