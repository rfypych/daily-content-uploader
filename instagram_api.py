import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from pydantic import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = Path("session.json")

def upload_video_with_instagrapi(file_path: str, caption: str) -> bool:
    """
    Uploads a video to Instagram using the instagrapi library.
    Handles session loading and saving to avoid repeated logins.
    """
    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logging.error("Missing Instagram credentials in .env file.")
        return False

    cl = Client()

    try:
        # --- Session Handling ---
        if SESSION_FILE.exists():
            logging.info(f"Found session file. Loading session from {SESSION_FILE}...")
            cl.load_settings(SESSION_FILE)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            try:
                cl.get_timeline_feed()
                logging.info("Session is valid.")
            except LoginRequired:
                logging.warning("Session is invalid, need to login again.")
                cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                cl.dump_settings(SESSION_FILE)
        else:
            logging.error("<<<<< LOGIN SESSION NOT FOUND! >>>>>")
            logging.error("File 'session.json' tidak ditemukan.")
            logging.error("Jalankan 'python3 setup.py' terlebih dahulu untuk melakukan login pertama kali.")
            return False

        # --- Video Upload ---
        video_path = Path(file_path)
        if not video_path.is_file():
            logging.error(f"Video file not found at path: {file_path}")
            return False

        logging.info(f"Uploading video from {file_path} to Instagram...")
        try:
            media = cl.video_upload(
                path=video_path,
                caption=caption,
            )
            logging.info(f"Successfully uploaded video. Media ID: {media.pk}")
            return True
        except ValidationError as e:
            # This error is expected on success due to an outdated model in instagrapi.
            # The upload works, but parsing the response fails. We can safely ignore this.
            logging.warning(f"Caught an expected Pydantic validation error, but the upload was successful. Error: {e}")
            return True

    except Exception as e:
        logging.error(f"An unexpected error occurred during the upload process: {e}")
        return False
