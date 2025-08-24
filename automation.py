from playwright.async_api import async_playwright
import asyncio
import logging
from pathlib import Path
from models import Content, Account
from database import SessionLocal
import os
from typing import Optional

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
        """Upload content to Instagram"""
        try:
            if not self.browser:
                await self.init_browser()
                
            page = await self.context.new_page()
            
            # Navigate to Instagram
            await page.goto('https://www.instagram.com/accounts/login/')
            await page.wait_for_load_state('networkidle')
            
            # Login
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)
            await page.click('button[type="submit"]')
            
            # Wait for login to complete
            await page.wait_for_url('https://www.instagram.com/', timeout=30000)
            
            # Handle "Save Info" dialog if appears
            try:
                await page.click('button:has-text("Not Now")', timeout=5000)
            except:
                pass
                
            # Handle notifications dialog if appears
            try:
                await page.click('button:has-text("Not Now")', timeout=5000)
            except:
                pass
            
            # Click create new post
            await page.click('svg[aria-label="New post"]')
            await page.wait_for_selector('input[type="file"]')
            
            # Upload file
            file_input = await page.query_selector('input[type="file"]')
            await file_input.set_input_files(content.file_path)
            
            # Wait for upload and click Next
            await page.wait_for_selector('button:has-text("Next")')
            await page.click('button:has-text("Next")')
            
            # Skip crop/filter steps
            await page.wait_for_selector('button:has-text("Next")')
            await page.click('button:has-text("Next")')
            
            # Add caption
            await page.wait_for_selector('textarea[aria-label="Write a caption..."]')
            await page.fill('textarea[aria-label="Write a caption..."]', content.caption)
            
            # Share post
            await page.click('button:has-text("Share")')
            
            # Wait for success
            await page.wait_for_selector('img[alt="Animated checkmark"]', timeout=30000)
            
            await page.close()
            logger.info(f"Successfully uploaded content {content.id} to Instagram")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload to Instagram: {str(e)}")
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
            # Get account credentials
            account = db.query(Account).filter(
                Account.platform == platform,
                Account.is_active == True
            ).first()
            
            if not account:
                logger.error(f"No active account found for platform: {platform}")
                return False
            
            # Upload based on platform
            if platform == "instagram":
                return await self.upload_to_instagram(content, account.username, account.password)
            elif platform == "tiktok":
                return await self.upload_to_tiktok(content, account.username, account.password)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return False
                
        finally:
            db.close()

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
