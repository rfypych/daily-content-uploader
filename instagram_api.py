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

SESSION_FILE = Path("session.json")

# --- Helper Function ---

def _get_instagrapi_client() -> Client:
    """
    Handles client instantiation and session loading.
    This function is designed to be run on the server. It will NOT
    attempt a full username/password login to avoid triggering challenges.
    It relies on a valid `session.json` file being present.
    """
    cl = Client()

    if not SESSION_FILE.exists():
        logging.error("CRITICAL: session.json not found. Please generate one on your local machine using `setup.py` and upload it to the server.")
        return None

    try:
        logging.info(f"Loading session from {SESSION_FILE}...")
        cl.load_settings(SESSION_FILE)

        # Perform a lightweight API call to check if the session is valid.
        # This will raise LoginRequired if the session is expired or invalid.
        cl.get_timeline_feed()

        logging.info("Session is valid.")
        return cl

    except LoginRequired:
        logging.error("CRITICAL: The session in session.json is invalid or expired. Please generate a new one on your local machine using `setup.py` and re-upload it.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during client session loading: {e}", exc_info=True)
        return None

# --- Upload Functions ---
# These functions now assume _get_instagrapi_client will provide a valid,
# logged-in client or None.

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
