from playwright.async_api import async_playwright
import asyncio
import logging
from pathlib import Path
from models import Content, Account
from database import SessionLocal
import os
from typing import Optional

# Import the new uploader
from instagram_api import upload_video_with_instagrapi

logger = logging.getLogger(__name__)

class ContentUploader:
    def __init__(self):
        self.browser = None
        self.context = None
        
    async def init_browser(self, headless: bool = True):
        """Initialize browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
    async def close_browser(self):
        """Close browser instance"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def upload_to_instagram(self, content: Content, username: str, password: str) -> bool:
        """
        Upload content to Instagram using the instagrapi library.
        The username and password arguments are ignored but kept for compatibility
        with the calling function.
        """
        logger.info("Starting Instagram upload using instagrapi...")
        try:
            loop = asyncio.get_running_loop()
            success = await loop.run_in_executor(
                None,  # Use the default executor
                upload_video_with_instagrapi,  # The synchronous function to call
                content.file_path,  # Arguments for the function
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
    
    async def upload_to_tiktok(self, content: Content, username: str, password: str) -> bool:
        """Upload content to TikTok"""
        try:
            if not self.browser:
                await self.init_browser()
                
            page = await self.context.new_page()
            
            # Navigate to TikTok
            await page.goto('https://www.tiktok.com/login')
            await page.wait_for_load_state('networkidle')
            
            # Click "Use phone / email / username"
            await page.click('a[href="/login/phone-or-email/email"]')
            
            # Login
            await page.fill('input[name="username"]', username)
            await page.fill('input[type="password"]', password)
            await page.click('button[type="submit"]')
            
            # Wait for login
            await page.wait_for_url('https://www.tiktok.com/foryou*', timeout=30000)
            
            # Navigate to upload page
            await page.goto('https://www.tiktok.com/upload')
            await page.wait_for_load_state('networkidle')
            
            # Upload file
            file_input = await page.query_selector('input[type="file"]')
            await file_input.set_input_files(content.file_path)
            
            # Wait for upload to complete
            await page.wait_for_selector('div[data-testid="video-preview"]', timeout=60000)
            
            # Add caption
            caption_selector = 'div[contenteditable="true"][data-text="Describe your video"]'
            await page.wait_for_selector(caption_selector)
            await page.click(caption_selector)
            await page.fill(caption_selector, content.caption)
            
            # Post video
            await page.click('button:has-text("Post")')
            
            # Wait for success
            await page.wait_for_url('https://www.tiktok.com/foryou*', timeout=30000)
            
            await page.close()
            logger.info(f"Successfully uploaded content {content.id} to TikTok")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload to TikTok: {str(e)}")
            return False
    
    async def upload_to_platform(self, content: Content, platform: str) -> bool:
        """Upload content to specified platform"""
        db = SessionLocal()
        try:
            # Handle 'both' platform by uploading to both Instagram and TikTok
            if platform == "both":
                instagram_success = await self._upload_to_single_platform(content, "instagram", db)
                tiktok_success = await self._upload_to_single_platform(content, "tiktok", db)
                return instagram_success or tiktok_success  # Success if at least one succeeds
            else:
                return await self._upload_to_single_platform(content, platform, db)
                
        finally:
            db.close()
    
    async def _upload_to_single_platform(self, content: Content, platform: str, db) -> bool:
        """Upload content to a single platform"""
        # Get account credentials
        account = db.query(Account).filter(
            Account.platform == platform,
            Account.is_active == True
        ).first()
        
        if not account:
            logger.error(f"No active account found for platform: {platform}")
            return False
        
        # Decrypt password
        password = account.get_password()
        if not password:
            logger.error(f"Could not decrypt password for {platform} account")
            return False
        
        # Upload based on platform
        if platform == "instagram":
            return await self.upload_to_instagram(content, account.username, password)
        elif platform == "tiktok":
            return await self.upload_to_tiktok(content, account.username, password)
        else:
            logger.error(f"Unsupported platform: {platform}")
            return False

# Utility function for testing
async def test_upload():
    """Test function untuk upload"""
    uploader = ContentUploader()
    try:
        await uploader.init_browser(headless=False)
        # Test code here
        await asyncio.sleep(5)
    finally:
        await uploader.close_browser()

if __name__ == "__main__":
    asyncio.run(test_upload())
