import asyncio
import logging
from models import Content
from database import SessionLocal

# Import the new specific uploader functions
from instagram_api import (
    upload_photo,
    upload_video,
    upload_reel,
    upload_album,
    upload_story
)

logger = logging.getLogger(__name__)

class ContentUploader:
    """
    Manages the content uploading process by routing to the correct uploader.
    """
    
    async def upload_to_instagram(self, content: Content) -> bool:
        """
        Dispatches the content to the correct instagrapi upload function
        based on the post_type stored in the Content object.
        """
        post_type = content.post_type
        logger.info(f"Dispatching content {content.id} for Instagram upload as type: '{post_type}'")

        # Define a mapping from post_type to the upload function
        upload_functions = {
            "photo": upload_photo,
            "video": upload_video,
            "reel": upload_reel,
            "album": upload_album,
            "story": upload_story,
        }

        upload_function = upload_functions.get(post_type)

        if not upload_function:
            logger.error(f"Unknown post type '{post_type}' for content ID {content.id}")
            return False

        try:
            loop = asyncio.get_running_loop()

            # Prepare arguments for the upload function
            if post_type == "album":
                # Album expects a list of paths
                args = [content.file_path.split(','), content.caption]
            elif post_type == "story":
                # Story needs a path, file_type, and the caption for the text sticker
                args = [content.file_path, content.file_type, content.caption]
            else:
                # Others need path and caption
                args = [content.file_path, content.caption]

            # Run the synchronous instagrapi function in a separate thread
            success = await loop.run_in_executor(
                None,       # Use the default executor
                upload_function, # The specific function to call (e.g., upload_photo)
                *args       # Unpack arguments
            )

            if success:
                logger.info(f"Successfully processed content {content.id} (type: {post_type}).")
            else:
                logger.error(f"Failed to process content {content.id} (type: {post_type}).")
            return success

        except Exception as e:
            logger.error(f"An unexpected error occurred during dispatch for content {content.id}: {e}")
            return False
    
    async def upload_to_platform(self, content: Content, platform: str) -> bool:
        """
        Routes the content upload to the appropriate platform-specific method.
        """
        # This function now only supports 'instagram' but is kept for structural consistency.
        if platform == "instagram":
            return await self.upload_to_instagram(content)
        else:
            logger.error(f"Unsupported platform: '{platform}'. This application is currently configured for Instagram only.")
            return False
