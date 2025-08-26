import os
import logging
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from pydantic import ValidationError

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = Path("session.json")

# --- Helper Function ---

def _get_instagrapi_client() -> Client:
    """
    Handles client instantiation and session login.
    Returns an authenticated client or None if login fails.
    """
    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logging.error("Missing Instagram credentials in .env file.")
        return None

    cl = Client()
    if not SESSION_FILE.exists():
        logging.error("<<<<< LOGIN SESSION NOT FOUND! >>>>>")
        logging.error("File 'session.json' tidak ditemukan.")
        logging.error("Jalankan 'python3 setup.py' terlebih dahulu untuk melakukan login pertama kali.")
        return None

    try:
        logging.info(f"Loading session from {SESSION_FILE}...")
        cl.load_settings(SESSION_FILE)
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.get_timeline_feed() # Test if the session is valid
        logging.info("Session is valid.")
        return cl
    except LoginRequired:
        logging.error("Session is invalid. Please run 'python3 setup.py' again to create a new session.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during client login: {e}")
        return None

# --- Upload Functions ---

def upload_photo(path: str, caption: str) -> bool:
    """Uploads a single photo to the Instagram feed."""
    cl = _get_instagrapi_client()
    if not cl:
        return False
    try:
        logging.info(f"Uploading photo from {path}...")
        cl.photo_upload(path, caption)
        logging.info("Photo uploaded successfully.")
        return True
    except ValidationError:
        logging.warning("Caught expected Pydantic validation error, but photo upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload photo: {e}")
        return False

def upload_video(path: str, caption: str) -> bool:
    """Uploads a single video to the Instagram feed (not as a Reel)."""
    cl = _get_instagrapi_client()
    if not cl:
        return False
    try:
        logging.info(f"Uploading video from {path}...")
        cl.video_upload(path, caption)
        logging.info("Video uploaded successfully.")
        return True
    except ValidationError:
        logging.warning("Caught expected Pydantic validation error, but video upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload video: {e}")
        return False

def upload_reel(path: str, caption: str) -> bool:
    """Uploads a video as a Reel."""
    cl = _get_instagrapi_client()
    if not cl:
        return False
    try:
        logging.info(f"Uploading Reel from {path}...")
        cl.reel_upload(path, caption)
        logging.info("Reel uploaded successfully.")
        return True
    except ValidationError:
        logging.warning("Caught expected Pydantic validation error, but reel upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload reel: {e}")
        return False

def upload_album(paths: List[str], caption: str) -> bool:
    """Uploads multiple photos/videos as a carousel/album."""
    cl = _get_instagrapi_client()
    if not cl:
        return False
    # Validate paths
    for p in paths:
        if not Path(p).is_file():
            logging.error(f"File not found in album paths: {p}")
            return False
    try:
        logging.info(f"Uploading album with {len(paths)} media files...")
        cl.album_upload(paths, caption)
        logging.info("Album uploaded successfully.")
        return True
    except ValidationError:
        logging.warning("Caught expected Pydantic validation error, but album upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload album: {e}")
        return False

def upload_story(path: str) -> bool:
    """Uploads a photo/video as a Story."""
    cl = _get_instagrapi_client()
    if not cl:
        return False
    try:
        logging.info(f"Uploading story from {path}...")
        cl.story_upload(path)
        logging.info("Story uploaded successfully.")
        return True
    except ValidationError:
        logging.warning("Caught expected Pydantic validation error, but story upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload story: {e}")
        return False
