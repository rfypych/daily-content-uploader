import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from automation import ContentUploader
from models import Content

class TestAutomationDispatcher(unittest.TestCase):

    def setUp(self):
        self.uploader = ContentUploader()
        self.loop = asyncio.get_event_loop()

    @patch('automation.upload_photo', return_value=True)
    def test_dispatches_to_upload_photo(self, mock_upload_photo):
        """Verify it calls the correct function for post_type 'photo'."""
        mock_content = Content(post_type='photo', file_path='/path/photo.jpg', caption='A photo')

        result = self.loop.run_until_complete(self.uploader.upload_to_instagram(mock_content))

        self.assertTrue(result)
        mock_upload_photo.assert_called_once_with('/path/photo.jpg', 'A photo')

    @patch('automation.upload_video', return_value=True)
    def test_dispatches_to_upload_video(self, mock_upload_video):
        """Verify it calls the correct function for post_type 'video'."""
        mock_content = Content(post_type='video', file_path='/path/video.mp4', caption='A video')

        result = self.loop.run_until_complete(self.uploader.upload_to_instagram(mock_content))

        self.assertTrue(result)
        mock_upload_video.assert_called_once_with('/path/video.mp4', 'A video')

    @patch('automation.upload_reel', return_value=True)
    def test_dispatches_to_upload_reel(self, mock_upload_reel):
        """Verify it calls the correct function for post_type 'reel'."""
        mock_content = Content(post_type='reel', file_path='/path/reel.mp4', caption='A reel')

        result = self.loop.run_until_complete(self.uploader.upload_to_instagram(mock_content))

        self.assertTrue(result)
        mock_upload_reel.assert_called_once_with('/path/reel.mp4', 'A reel')

    @patch('automation.upload_album', return_value=True)
    def test_dispatches_to_upload_album(self, mock_upload_album):
        """Verify it calls the correct function for post_type 'album'."""
        mock_content = Content(
            post_type='album',
            file_path='/path/img1.jpg,/path/vid1.mp4',
            caption='An album'
        )

        result = self.loop.run_until_complete(self.uploader.upload_to_instagram(mock_content))

        self.assertTrue(result)
        # Check that the file_path string was correctly split into a list
        mock_upload_album.assert_called_once_with(['/path/img1.jpg', '/path/vid1.mp4'], 'An album')

    @patch('automation.upload_story', return_value=True)
    def test_dispatches_to_upload_story(self, mock_upload_story):
        """Verify it calls the correct function for post_type 'story'."""
        mock_content = Content(
            post_type='story',
            file_path='/path/story.jpg',
            file_type='image/jpeg',
            caption='A story caption' # Caption should be passed
        )

        result = self.loop.run_until_complete(self.uploader.upload_to_instagram(mock_content))

        self.assertTrue(result)
        # Check that file_path and file_type are passed
        mock_upload_story.assert_called_once_with('/path/story.jpg', 'image/jpeg')

if __name__ == '__main__':
    unittest.main()
