import os
from fastapi import UploadFile

# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mp4"}

def validate_file(file: UploadFile) -> bool:
    """
    Validates a file based on its extension.
    """
    if not file.filename:
        return False

    file_extension = file.filename.rsplit('.', 1)[-1].lower()

    if file_extension in ALLOWED_EXTENSIONS:
        return True

    return False
