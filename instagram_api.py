import os
import logging
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

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
    This function will attempt a full login if the session is invalid.
    """
    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logging.error("Missing Instagram credentials in .env file.")
        return None

    cl = Client()

    if SESSION_FILE.exists():
        logging.info(f"Loading session from {SESSION_FILE}...")
        cl.load_settings(SESSION_FILE)

    try:
        # This login call will use the session if it's loaded and valid,
        # otherwise it will perform a full login with username/password.
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.get_timeline_feed() # Verify session is truly working
        logging.info("Session is valid and login successful.")
        return cl
    except LoginRequired:
        logging.error("Session is invalid. A new login attempt will be made, which may require a challenge code if run on a new server.")
        # The login call above will handle the re-login attempt.
        # If it fails again, it will raise an exception.
        return None # Should not be reached if login raises
    except Exception as e:
        logging.error(f"An unexpected error occurred during client login: {e}", exc_info=True)
        return None

# --- Upload Functions ---

def upload_photo(path: str, caption: str) -> bool:
    logging.info(f"Attempting to upload photo from {path}...")
    cl = _get_instagrapi_client()
    if not cl:
        return False
    try:
        media = cl.photo_upload(path=path, caption="")
        if caption:
            logging.info(f"Editing media {media.pk} to set caption.")
            cl.media_edit(media.pk, caption)
        logging.info(f"Successfully uploaded photo {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload photo: {e}", exc_info=True)
        return False

def upload_video(path: str, caption: str) -> bool:
    logging.info(f"Attempting to upload video from {path}...")
    cl = _get_instagrapi_client()
    if not cl:
        return False
    try:
        media = cl.video_upload(path=path, caption="")
        if caption:
            logging.info(f"Editing media {media.pk} to set caption.")
            cl.media_edit(media.pk, caption)
        logging.info(f"Successfully uploaded video {media.pk}.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload video: {e}", exc_info=True)
        return False

def upload_reel(path: str, caption: str) -> bool:
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
    logging.info(f"Attempting to upload album with {len(paths)} media...")
    cl = _get_instagrapi_client()
    if not cl:
        return False
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
