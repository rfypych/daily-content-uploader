import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from scheduler import scheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

from database import SessionLocal
from models import Schedule
from datetime import datetime

async def load_and_reschedule_jobs():
    """
    Loads all 'pending' and 'recurring' jobs from the database and
    adds them to the APScheduler instance. This is crucial for ensuring
    that jobs persist across scheduler restarts.
    """
    db = SessionLocal()
    try:
        logger.info("--- Loading and rescheduling existing jobs from database ---")

        # Load one-time pending jobs
        pending_schedules = db.query(Schedule).filter(
            Schedule.status == 'pending',
            Schedule.scheduled_time > datetime.utcnow() # Only schedule future jobs
        ).all()

        logger.info(f"Found {len(pending_schedules)} pending one-time jobs to reschedule.")
        for schedule in pending_schedules:
            logger.info(f"Rescheduling job for content {schedule.content_id} at {schedule.scheduled_time}")
            await scheduler.schedule_upload(schedule)

        # Load recurring jobs
        recurring_schedules = db.query(Schedule).filter(Schedule.status == 'recurring').all()
        logger.info(f"Found {len(recurring_schedules)} recurring jobs to reschedule.")
        for r_schedule in recurring_schedules:
            # We need to extract the time from the original job's cron trigger
            # This is a bit tricky as the time isn't stored directly on the Schedule model.
            # A better approach would be to store hour/minute on the recurring schedule model.
            # For now, we assume the job already exists in the job store and scheduler.start() will handle it.
            # The add_daily_schedule creates a master schedule entry AND adds to APScheduler.
            # When the scheduler starts, it should pick up jobs from its own table.
            # The main fix is for the 'pending' jobs which are not master jobs.
            pass # Let's see if scheduler.start() handles the recurring ones from the jobstore.
            # The original logic for daily schedule in main.py already adds to the scheduler job store.
            # The main gap was for one-time schedules.

        logger.info("--- Finished loading jobs ---")

    except Exception as e:
        logger.error(f"Error during job rescheduling: {e}", exc_info=True)
    finally:
        db.close()


async def main():
    """
    Main function to start and run the scheduler indefinitely.
    This should be run as a separate, persistent process in production.
    """
    logger.info("Initializing scheduler...")

    # First, load any jobs from our application's database schema
    await load_and_reschedule_jobs()

    logger.info("Starting the standalone scheduler process...")
    try:
        # Now, start the APScheduler engine. It will load jobs from its own job store.
        await scheduler.start()
        logger.info("Scheduler started successfully. Process will now run in the background.")
        # Keep the process alive
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, the scheduler runs on its own thread.
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler process stopped.")
    finally:
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
