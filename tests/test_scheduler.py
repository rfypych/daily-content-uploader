import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# It's good practice to set the path for module discovery
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scheduler import execute_recurring_job
from models import Schedule, Content

class TestSchedulerLogic(unittest.TestCase):

    @patch('scheduler.SessionLocal')
    @patch('scheduler.ContentUploader')
    def test_execute_recurring_job_with_day_counter(self, MockContentUploader, MockSessionLocal):
        # --- 1. Setup Mocks ---

        # Mock the ContentUploader instance and its method
        mock_uploader_instance = MockContentUploader.return_value
        mock_uploader_instance.upload_to_platform = AsyncMock(return_value=True)

        # Mock the database session and its query capabilities
        mock_db_session = MockSessionLocal.return_value

        # Mock the master schedule object that the DB will return
        mock_master_schedule = Schedule(
            id=1,
            content_id=101,
            status='recurring',
            use_day_counter=True,
            day_counter=5
        )

        # Mock the content object that the DB will return
        mock_content = Content(
            id=101,
            caption="This is the original caption."
        )

        # Configure the mock query chain
        mock_query = MagicMock()

        # When filter is called for the schedule, return the schedule mock
        mock_query.filter.return_value.first.side_effect = [
            mock_master_schedule, # First call gets the schedule
            mock_content        # Second call gets the content
        ]
        mock_db_session.query.return_value = mock_query

        # --- 2. Execute the function under test ---

        # We need to run the async function in an event loop
        asyncio.run(execute_recurring_job(recurring_schedule_id=1))

        # --- 3. Assertions ---

        # Assert that the uploader was called
        mock_uploader_instance.upload_to_platform.assert_called_once()

        # Get the arguments that the uploader was called with
        # The first argument is the 'content' object
        call_args, call_kwargs = mock_uploader_instance.upload_to_platform.call_args
        called_with_content = call_args[0]

        # Assert the caption was correctly modified
        expected_caption = "Day 5 - This is the original caption."
        self.assertEqual(called_with_content.caption, expected_caption)

        # Assert that the day_counter on the original schedule object was incremented
        self.assertEqual(mock_master_schedule.day_counter, 6)

        # Assert that db.commit() was called to save the incremented counter
        mock_db_session.commit.assert_called()

if __name__ == '__main__':
    unittest.main()
