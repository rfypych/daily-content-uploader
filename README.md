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

This application uses a robust workflow to avoid triggering Instagram's security measures. The setup is divided into two parts: a one-time setup on your **local computer** and the deployment on your **server**.

### **Part 1: Session Generation (On Your Local Computer)**

The most important step is to generate a `session.json` file on a trusted machine (your personal computer) to avoid server-based login challenges.

1.  **Clone the Repository Locally:**
    ```bash
    git clone https://github.com/your-repo/your-project.git
    cd daily-content-uploader
    ```

2.  **Install Dependencies Locally:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Local Environment:** Create a `.env` file from the example.
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file and fill in your `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`.

4.  **Run Interactive Setup Locally:** Run the `setup.py` script.
    ```bash
    python3 setup.py
    ```
    - The script will guide you through the Instagram login process.
    - **Enter the 2FA code** sent to your email when prompted.
    - Upon success, a `session.json` file will be created in your project directory. This file is crucial.

### **Part 2: Server Deployment**

Now, you will deploy the application code and the generated session file to your server.

1.  **Upload Project Files:** Upload all project files (except `session.json` for now) to your server (e.g., in `/www/wwwroot/your.domain.com`).

2.  **Configure Server Environment:**
    - Create a `.env` file on the server (`cp .env.example .env`).
    - Fill in your `DATABASE_URL`.
    - Set the `WEB_USERNAME` and `WEB_PASSWORD` for your dashboard login.
    - Set your `TIMEZONE` (e.g., `Asia/Jakarta`).
    - **Leave `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` blank on the server.** This is important for security.

3.  **Upload the Session File:** Securely upload the `session.json` file you generated in Part 1 to the project directory on your server.

4.  **Initialize Server Database:**
    - SSH into your server and navigate to the project directory.
    - Run the setup script **without the login part** to initialize the database and create the web user.
    ```bash
    python3 setup.py
    ```
    *(Because INSTAGRAM_USERNAME is blank in the server's .env, it will skip the interactive login part).*

5.  **Run the Application:**
    Run both the web server and the scheduler as persistent background services.
    -   **Web Server:**
        ```bash
        nohup gunicorn -c gunicorn_config.py main:app > gunicorn.log 2>&1 &
        ```
    -   **Scheduler Service:**
        ```bash
        nohup python3 run_scheduler.py > scheduler.log 2>&1 &
        ```

You can now access your dashboard at `http://your_server_address:PORT` and log in with your `WEB_USERNAME` and `WEB_PASSWORD`.

---

## 🆘 **Troubleshooting**

*   **`Session is invalid` Error:** Your `session.json` has expired or been invalidated by Instagram. You must repeat **Part 1** on your local machine to generate a new `session.json` and then re-upload only that file to your server.
*   **Database Error (e.g., "Unknown column"):** This can happen after a code update. To fix this, you may need to reset your database. Run the setup script with the `--reset-db` flag on your server. **Warning: This will delete all your existing content and schedules.**
    ```bash
    python3 setup.py --reset-db
    ```

---

**Happy Content Creating! 🎉**
