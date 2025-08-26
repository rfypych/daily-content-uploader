import asyncio
import logging
from models import Content
from database import SessionLocal

# Import the new uploader
from instagram_api import upload_video_with_instagrapi

logger = logging.getLogger(__name__)

class ContentUploader:
    """
    Manages the content uploading process.
    Currently only supports Instagram.
    """
    
    async def upload_to_instagram(self, content: Content) -> bool:
        """
        Uploads content to Instagram using the instagrapi library.
        """
        logger.info("Starting Instagram upload using instagrapi...")
        try:
            loop = asyncio.get_running_loop()
            # Run the synchronous instagrapi function in a separate thread
            success = await loop.run_in_executor(
                None,
                upload_video_with_instagrapi,
                content.file_path,
                content.caption
            )
            if success:
                logger.info(f"Successfully uploaded content {content.id} to Instagram via instagrapi.")
            else:
                logger.error(f"Failed to upload content {content.id} to Instagram via instagrapi.")
            return success
        except Exception as e:
            logger.error(f"An unexpected error occurred during instagrapi integration: {e}")
            return False
    
    async def upload_to_platform(self, content: Content, platform: str) -> bool:
        """
        Routes the content upload to the appropriate platform-specific method.
        """
        db = SessionLocal()
        try:
            # The 'both' option is kept for potential future expansion,
            # but currently only routes to Instagram.
            if platform in ["instagram", "both"]:
                return await self.upload_to_instagram(content)
            else:
                logger.error(f"Unsupported platform: '{platform}'. This application is currently configured for Instagram only.")
                return False
        finally:
            db.close()

# Note: The original _upload_to_single_platform, upload_to_tiktok,
# and browser-related methods have been removed as they are no longer used.
# The test_upload function is also removed as it was for the old implementation.
