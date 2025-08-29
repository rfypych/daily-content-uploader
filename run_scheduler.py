import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables first
load_dotenv()

from scheduler import scheduler, execute_scheduled_upload, execute_recurring_job
from database import SessionLocal
from models import Schedule

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def discover_and_schedule_jobs():
    """
    Periodically discovers new schedule 'intents' from the database
    and adds them to the live APScheduler.
    """
    db = SessionLocal()
    try:
        logger.info("Checking for new jobs to schedule...")

        # Find all schedule intents that haven't been processed yet
        new_schedules = db.query(Schedule).filter(Schedule.is_scheduled == False).all()

        if not new_schedules:
            logger.info("No new jobs found.")
            return

        logger.info(f"Found {len(new_schedules)} new jobs to add to the scheduler.")

        for schedule in new_schedules:
            job_id = None
            try:
                if schedule.status == 'pending':
                    # This is a one-time job
                    job_id = f"upload_{schedule.id}"
                    scheduler.scheduler.add_job(
                        func=execute_scheduled_upload,
                        trigger='date',
                        run_date=schedule.scheduled_time,
                        args=[schedule.id],
                        id=job_id,
                        replace_existing=True
                    )
                    logger.info(f"Scheduled one-time job '{job_id}' for {schedule.scheduled_time}.")

                elif schedule.status == 'recurring':
                    # This is a recurring (daily) job
                    job_id = f"daily_{schedule.id}"
                    user_timezone = os.getenv('TIMEZONE', 'UTC')
                    scheduler.scheduler.add_job(
                        func=execute_recurring_job,
                        trigger='cron',
                        hour=schedule.hour,
                        minute=schedule.minute,
                        timezone=user_timezone,
                        args=[schedule.id],
                        id=job_id,
                        replace_existing=True
                    )
                    logger.info(f"Scheduled recurring job '{job_id}' for {schedule.hour:02d}:{schedule.minute:02d} ({user_timezone}).")

                # If scheduling was successful, mark it as processed
                schedule.is_scheduled = True
                db.commit()
                logger.info(f"Successfully processed and marked schedule {schedule.id}.")

            except Exception as e:
                logger.error(f"Failed to schedule job for schedule_id {schedule.id}: {e}", exc_info=True)
                # We don't commit here, so it can be picked up on the next run

    finally:
        db.close()

async def main():
    """
    Main function to start the scheduler and run the discovery loop.
    """
    logger.info("--- Starting Scheduler Service ---")

    # Start the underlying APScheduler engine. It will run in the background.
    await scheduler.start()

    try:
        # This is the main service loop
        while True:
            await discover_and_schedule_jobs()
            logger.info("Scheduler service sleeping for 60 seconds...")
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler service shutting down.")
    finally:
        await scheduler.stop()

if __name__ == "__main__":
    # This check is important for multiprocessing safety
    asyncio.run(main())
