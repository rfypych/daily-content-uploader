import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# It's good practice to set the path for module discovery
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheduler import execute_upload_logic
from models import Schedule, Content

class TestSchedulerLogic(unittest.TestCase):

    @patch('scheduler.ContentUploader')
    def test_execute_upload_logic_for_recurring_job(self, MockContentUploader):
        # --- 1. Setup Mocks ---

        # Mock the ContentUploader instance and its method
        mock_uploader_instance = MockContentUploader.return_value
        mock_uploader_instance.upload_to_platform = AsyncMock(return_value=True)

        # Mock the schedule and content objects to be passed to the function
        mock_schedule = Schedule(
            id=1,
            status='recurring',
            use_day_counter=True,
            day_counter=5
        )
        mock_content = Content(
            id=101,
            caption="This is the original caption."
        )

        # --- 2. Execute the function under test ---

        # We need to run the async function in an event loop
        result = asyncio.run(execute_upload_logic(mock_schedule, mock_content))

        # --- 3. Assertions ---

        # Assert that the function returned True for success
        self.assertTrue(result)

        # Assert that the uploader was called
        mock_uploader_instance.upload_to_platform.assert_called_once()

        # Get the arguments that the uploader was called with
        # The first argument is the 'content' object
        call_args, call_kwargs = mock_uploader_instance.upload_to_platform.call_args
        called_with_content = call_args[0]

        # Assert the caption was correctly modified
        expected_caption = "Day 5 This is the original caption."
        self.assertEqual(called_with_content.caption, expected_caption)

        # Assert that the day_counter on the original schedule object was NOT incremented by this function
        self.assertEqual(mock_schedule.day_counter, 5)

if __name__ == '__main__':
    unittest.main()
