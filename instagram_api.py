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
    Handles client instantiation, session loading, and login.
    Returns a logged-in client instance or None on failure.
    """
    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logging.error("Missing Instagram credentials in .env file.")
        return None

    cl = Client()

    if not SESSION_FILE.exists():
        logging.error("session.json not found. Please run 'python3 setup.py' first.")
        return None

    try:
        logging.info(f"Loading session from {SESSION_FILE}...")
        cl.load_settings(SESSION_FILE)
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        # It's good practice to make a lightweight API call to check if the session is valid.
        cl.get_timeline_feed(amount=1)
        logging.info("Session is valid and login successful.")
        return cl
    except LoginRequired:
        logging.error("Session is invalid. Please run 'python3 setup.py' again to refresh it.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during client login: {e}", exc_info=True)
        return None

# --- Upload Functions ---

def upload_photo(path: str, caption: str) -> bool:
    """
    Uploads a single photo.
    Uses the 'upload then edit caption' method for maximum reliability.
    """
    logging.info(f"Attempting to upload photo from {path}...")
    cl = _get_instagrapi_client()
    if not cl:
        return False

    try:
        media = cl.photo_upload(path=path, caption="") # Upload with empty caption first
        if caption:
            logging.info(f"Editing media {media.pk} to set caption.")
            cl.media_edit(media.pk, caption)
        logging.info(f"Successfully uploaded photo {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload photo: {e}", exc_info=True)
        return False

def upload_video(path: str, caption: str) -> bool:
    """
    Uploads a single video.
    Uses the 'upload then edit caption' method for maximum reliability.
    """
    logging.info(f"Attempting to upload video from {path}...")
    cl = _get_instagrapi_client()
    if not cl:
        return False

    try:
        media = cl.video_upload(path=path, caption="") # Upload with empty caption first
        if caption:
            logging.info(f"Editing media {media.pk} to set caption.")
            cl.media_edit(media.pk, caption)
        logging.info(f"Successfully uploaded video {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload video: {e}", exc_info=True)
        return False

def upload_reel(path: str, caption: str) -> bool:
    """
    Uploads a video as a Reel.
    The `clip_upload` method is generally reliable with captions directly.
    """
    logging.info(f"Attempting to upload Reel from {path}...")
    cl = _get_instagrapi_client()
    if not cl:
        return False

    try:
        media = cl.clip_upload(path=path, caption=caption)
        logging.info(f"Successfully uploaded Reel {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload Reel: {e}", exc_info=True)
        return False

def upload_album(paths: List[str], caption: str) -> bool:
    """
    Uploads multiple photos/videos as a carousel/album.
    The `album_upload` method is generally reliable with captions directly.
    """
    logging.info(f"Attempting to upload album with {len(paths)} media...")
    cl = _get_instagrapi_client()
    if not cl:
        return False

    # Validate that all paths exist before attempting upload
    validated_paths = [p for p in paths if Path(p).is_file()]
    if len(validated_paths) != len(paths):
        logging.error("One or more files not found in album paths. Aborting upload.")
        return False

    try:
        media = cl.album_upload(paths=validated_paths, caption=caption)
        logging.info(f"Successfully uploaded album {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload album: {e}", exc_info=True)
        return False

def upload_story(path: str, file_type: str) -> bool:
    """
    Uploads a photo or video as a Story. Captions are not supported here.
    """
    logging.info(f"Attempting to upload story from {path}...")
    cl = _get_instagrapi_client()
    if not cl:
        return False

    try:
        if "image" in file_type:
            media = cl.photo_upload_to_story(path=path)
        elif "video" in file_type:
            media = cl.video_upload_to_story(path=path)
        else:
            logging.error(f"Unsupported file type for story: {file_type}")
            return False
        logging.info(f"Successfully uploaded story {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload story: {e}", exc_info=True)
        return False
