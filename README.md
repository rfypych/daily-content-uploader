<div align="center">

[**English**](#) | [**Bahasa Indonesia**](./README_ID.md)

# 🚀 Instagram Content Uploader

### *A Simple and Powerful Instagram Automation Tool*

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![instagrapi](https://img.shields.io/badge/instagrapi-2.2.1-purple.svg)](https://github.com/subzeroid/instagrapi)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🎯 Set & Forget - Upload and schedule Instagram content 24/7 without manual intervention!**

[🚀 Quick Start Guide](#-quick-start--setup-guide) • [✨ Key Features](#-key-features)

---

</div>

## ✨ **Key Features**

<div align="center">

| 🎯 **Core Features** | 🔧 **Technical Features** | 🚀 **Advanced Features** |
|:---:|:---:|:---:|
| 📱 **Instagram Automation**<br/>Focus on a single platform | 🤖 **Private API**<br/>instagrapi Engine | ⏰ **Smart Scheduler**<br/>APScheduler Integration |
| 📅 **Auto Scheduling**<br/>Set & Forget | 🗄️ **Database Management**<br/>SQLite & MySQL Support | 🔐 **Session Management**<br/>Secure & efficient login |
| 🎨 **Web Dashboard**<br/>Modern UI/UX | 🌐 **Production Ready**<br/>Gunicorn + Web Server | 📊 **Analytics & Monitoring**<br/>Real-time Status |

</div>

---

## 🚀 **Quick Start & Setup Guide**

Follow these two main steps to get the application running.

### **Step 1: Initial Setup (One-Time Only)**

This step prepares the configuration, database, and most importantly, performs the first-time login to Instagram to save your session.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rfypych/daily-content-uploader.git
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
    Open the `.env` file and fill in your Instagram credentials (`INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`). You can also change the `PORT` if needed.

4.  **Run the Interactive Setup Script:** Run the `setup.py` script from your terminal.
    ```bash
    python3 setup.py
    ```
    - This script will create the database (`daily_content.db`).
    - It will then attempt to log in to Instagram.
    - **IMPORTANT:** Instagram will likely send a 2FA verification code to your email. The script will pause and prompt you to enter the 6-digit code in the terminal.
    - After the correct code is entered, the login will succeed, and the script will create a `session.json` file. This file is your key to automatic logins in the future.

Once `setup.py` is complete and `session.json` has been successfully created, you are ready for the next step.

### **Step 2: Running the Application**

The application consists of two main components that must be run separately in production: the **Web Server** and the **Scheduler**.

-   **Web Server:** Handles the user interface and API requests.
-   **Scheduler:** Runs in the background to process scheduled uploads.

**For Development:**
You can run both processes in two separate terminal windows.
-   **Terminal 1 (Web Server):**
    ```bash
    python3 main.py
    ```
-   **Terminal 2 (Scheduler):**
    ```bash
    python3 run_scheduler.py
    ```

**For Production:**
It is crucial to run both as persistent background services using a process manager like `pm2` or `supervisor`.
-   **Process 1 (Web Server with Gunicorn):**
    ```bash
    gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:2009
    ```
-   **Process 2 (Scheduler):**
    ```bash
    python3 run_scheduler.py
    ```
You can now access the web dashboard at `http://your_server_address:PORT` to start uploading and scheduling content. The scheduler will automatically pick up jobs from the database.

---

### 📖 **Dashboard Usage Guide**

-   **Upload Content:** Click the "Upload Konten" (Upload Content) button. Fill out the form, select a video/image file, write a caption, and click "Upload".
-   **Post Immediately:** In the "Konten Terbaru" (Recent Content) list, click the "share" icon (arrow) to publish the content directly to Instagram.
-   **Schedule a Post:** Set a schedule when uploading or create a daily schedule from the "Jadwal Harian" (Daily Schedule) menu.

<details>
<summary><b>aaPanel Deployment Guide (Click to expand)</b></summary>

Here is a step-by-step guide to deploy this application on your server using aaPanel.

**1. Preparation in aaPanel:**
   - Open your aaPanel.
   - Go to the **Website** menu -> **Add site**.
   - Create a new website for your domain or subdomain.

**2. Upload Code:**
   - Go to the **Files** menu.
   - Navigate to the root directory of the website you just created (e.g., `/www/wwwroot/domain.com`).
   - Delete default files like `index.html`.
   - Upload all files from this repository to that directory.

**3. Setup Python Environment:**
   - Go to the **App Store** menu and install **Python Manager**.
   - Inside Python Manager, install a suitable Python version (e.g., 3.10 or 3.11).
   - Go back to your **Website** settings, select your site, and click on **Python Project**.
   - Click **Add Python project**.
   - Select the Python version you installed.
   - **Framework:** Choose `gunicorn`.
   - **Startup file/directory:** Enter `main.py`.
   - Click **Confirm**. This will create a virtual environment for you.

**4. Install Dependencies:**
   - After the Python project is created, aaPanel will provide the path to your virtual environment.
   - Open the **Terminal** in aaPanel.
   - Activate the virtual environment with the provided command, e.g., `source /www/wwwroot/domain.com/pyenv/bin/activate`.
   - Run the following command to install all required libraries:
     ```bash
     pip install -r requirements.txt
     ```

**5. Configuration and Initial Setup:**
   - Still in the **Terminal** (with the virtual environment active):
     - Create the `.env` file: `cp .env.example .env`
     - Edit the `.env` file with nano: `nano .env`. Enter your Instagram credentials, then save (Ctrl+X, Y, Enter).
     - Run the interactive setup for the first-time login:
       ```bash
       python3 setup.py
       ```
     - Follow the prompt to enter the 2FA code from your email.

**6. Run the Application:**
   - In the aaPanel **Python Project** manager for your site, configure the startup command to be the Gunicorn command:
     ```
     gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:2009
     ```
   - Click **Start** or **Restart**. This runs the web server.
   - Now, open the **Terminal** again (ensure the virtual environment is active: `source .../bin/activate`).
   - Run the scheduler as a persistent background process. The best way is using a process manager like `pm2` or `supervisor`. If you don't have one, you can use `nohup` for a simple setup:
     ```bash
     nohup python3 run_scheduler.py &
     ```
   - Your application is now fully running.

</details>

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
