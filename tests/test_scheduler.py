import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# It's good practice to set the path for module discovery
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run_scheduler import check_and_run_schedules
from models import Schedule, Content
from datetime import datetime, timedelta
import pytz

class TestSchedulerLogic(unittest.TestCase):

    @patch('run_scheduler.SessionLocal')
    @patch('run_scheduler.execute_upload_logic', new_callable=AsyncMock)
    @patch('run_scheduler.datetime')
    def test_check_and_run_schedules_recurring_job(self, mock_datetime, mock_execute_upload_logic, MockSessionLocal):
        # --- 1. Setup Mocks ---
        mock_db_session = MockSessionLocal.return_value
        mock_execute_upload_logic.return_value = True

        # Mock the current time to ensure the job is due
        user_timezone = pytz.timezone(os.getenv('TIMEZONE', 'UTC'))
        mock_now = datetime(2023, 1, 1, 10, 30).astimezone(user_timezone)
        mock_datetime.now.return_value = mock_now

        # Mock the schedule object that the DB will return
        mock_schedule = Schedule(
            id=1,
            content_id=101,
            status='recurring',
            hour=10,
            minute=30,
            use_day_counter=True,
            day_counter=5,
            last_run_at=mock_now - timedelta(days=1)
        )

        mock_db_session.query.return_value.filter.return_value.all.return_value = [mock_schedule]

        # --- 2. Execute the function under test ---
        asyncio.run(check_and_run_schedules())

        # --- 3. Assertions ---
        mock_execute_upload_logic.assert_called_once_with(mock_db_session, mock_schedule)

        self.assertEqual(mock_schedule.day_counter, 6)
        self.assertEqual(mock_schedule.last_run_at.date(), mock_now.date())
        mock_db_session.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
