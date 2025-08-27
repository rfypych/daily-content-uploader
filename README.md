# Social Media Uploader

This is a simple web application to upload and schedule posts to social media platforms. It uses a Flask web interface and a background scheduler to automate posting.

**DISCLAIMER:** This application interacts with the private, internal APIs of Instagram. This is against their Terms of Service and can result in temporary or permanent blocks of your account. Use this tool at your own risk. The TikTok functionality is currently non-operational.

## Features

*   **Web-Based UI:** An easy-to-use dashboard for uploading and scheduling content.
*   **Instagram Support:**
    *   Upload single Photos.
    *   Upload single Videos.
    *   Upload videos as Reels.
    *   Upload multiple images/videos as an Album (Carousel).
    *   Upload photos or videos to your Story.
*   **Scheduling:** Schedule posts for a future date and time.
*   **Dynamic Captions:** Optional "Day X" feature to automatically number your daily posts.

## Setup Instructions

Follow these steps carefully to get the application running.

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Install Dependencies

It is highly recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Credentials

Create a `.env` file by copying the example file.

```bash
cp .env.example .env
```

Now, open the `.env` file with a text editor and add your Instagram username and password:

```
INSTAGRAM_USERNAME="your_instagram_username"
INSTAGRAM_PASSWORD="your_instagram_password"
```

### 4. Generate Instagram Session (CRITICAL STEP)

Because this tool logs in non-interactively, you must create a session file first. This step handles Instagram's two-factor authentication (2FA) challenge. You only need to do this once.

Run the setup script:

```bash
python3 setup.py
```

The script will prompt you for a 2FA code that Instagram sends to your email or authenticator app. Enter it when asked. This will create a `session.json` file, allowing the application to log in automatically in the future.

## Running the Application

This application requires two separate processes to be running simultaneously in two different terminal windows.

### Terminal 1: Run the Web Server

The web server handles the user interface and API requests. We use Gunicorn with a Uvicorn worker to run our FastAPI application.

```bash
gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
```

You can now access the web dashboard by navigating to `http://localhost:8000` in your web browser.

### Terminal 2: Run the Scheduler

The scheduler is responsible for executing the scheduled posts at their designated time.

```bash
python3 run_scheduler.py
```

This process must remain running in the background for schedules to work.

## Usage

1.  Navigate to `http://localhost:8000`.
2.  Use the form to select the post type (Photo, Video, Reel, etc.).
3.  Upload your media file(s).
4.  Write your caption.
5.  (Optional) Check the "Daily Schedule" box and enter a start date and day number for dynamic "Day X" captions.
6.  (Optional) Set a future date and time to schedule the post.
7.  Click "Upload".

## Known Issues

*   **TikTok Uploads:** The TikTok functionality is **completely broken** due to CAPTCHA and login challenges. It is disabled.
*   **Story Captions:** Instagram's private API (via `instagrapi`) does not support adding a text caption directly when uploading a story. The caption field is ignored for Story uploads.
*   **Session Invalidation:** Your `session.json` may occasionally become invalid. If you encounter login errors, simply delete `session.json` and run `python3 setup.py` again.
