import os
import logging
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.types import StoryText
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
    """Handles client instantiation and session login."""
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
        cl.get_timeline_feed()
        logging.info("Session is valid.")
        return cl
    except LoginRequired:
        logging.error("Session is invalid. Please run 'python3 setup.py' again.")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during client login: {e}")
        return None

# --- Upload Functions ---

def upload_photo(path: str, caption: str) -> bool:
    """Uploads a single photo to the Instagram feed."""
    cl = _get_instagrapi_client()
    if not cl: return False
    try:
        logging.info(f"Uploading photo from {path} with caption: '{caption[:50]}...'")
        cl.photo_upload(path, caption)
        return True
    except ValidationError:
        logging.warning("Caught Pydantic error, but assuming photo upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload photo: {e}")
        return False

def upload_video(path: str, caption: str) -> bool:
    """Uploads a single video to the Instagram feed."""
    cl = _get_instagrapi_client()
    if not cl: return False
    try:
        logging.info(f"Uploading video from {path} with caption: '{caption[:50]}...'")
        cl.video_upload(path, caption)
        return True
    except ValidationError:
        logging.warning("Caught Pydantic error, but assuming video upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload video: {e}")
        return False

def upload_reel(path: str, caption: str) -> bool:
    """Uploads a video as a Reel."""
    cl = _get_instagrapi_client()
    if not cl: return False
    try:
        logging.info(f"Uploading Reel from {path} with caption: '{caption[:50]}...'")
        cl.clip_upload(path, caption)
        return True
    except ValidationError:
        logging.warning("Caught Pydantic error, but assuming reel upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload reel: {e}")
        return False

def upload_album(paths: List[str], caption: str) -> bool:
    """Uploads multiple photos/videos as a carousel/album."""
    cl = _get_instagrapi_client()
    if not cl: return False
    validated_paths = [p for p in paths if Path(p).is_file()]
    if len(validated_paths) != len(paths):
        logging.error("One or more files not found in album paths.")
        return False
    try:
        logging.info(f"Uploading album with {len(paths)} media and caption: '{caption[:50]}...'")
        cl.album_upload(validated_paths, caption)
        return True
    except ValidationError:
        logging.warning("Caught Pydantic error, but assuming album upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload album: {e}")
        return False

def upload_story(path: str, file_type: str, caption: str) -> bool:
    """Uploads a photo/video as a Story, with an optional caption as a text sticker."""
    cl = _get_instagrapi_client()
    if not cl: return False

    # Create a text sticker if caption is provided
    stickers = []
    if caption:
        logging.info(f"Adding caption as a text sticker: '{caption[:50]}...'")
        stickers.append(StoryText(text=caption))

    try:
        logging.info(f"Uploading story from {path}...")
        if "image" in file_type:
            cl.photo_upload_to_story(path, extra_data={'stickers': [s.dict() for s in stickers]})
        elif "video" in file_type:
            cl.video_upload_to_story(path, extra_data={'stickers': [s.dict() for s in stickers]})
        else:
            logging.error(f"Unsupported file type for story: {file_type}")
            return False
        logging.info("Story uploaded successfully.")
        return True
    except ValidationError:
        logging.warning("Caught Pydantic error, but assuming story upload was successful.")
        return True
    except Exception as e:
        logging.error(f"Failed to upload story: {e}")
        return False
