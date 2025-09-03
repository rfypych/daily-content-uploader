import asyncio
import logging
import os
import pytz
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables first
load_dotenv()

from scheduler import execute_upload_logic
from database import SessionLocal
from models import Schedule

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_and_run_schedules():
    """
    The core function of the custom scheduler.
    - Fetches all active schedules.
    - Checks if they are due.
    - Executes them and updates their state in the database.
    """
    db = SessionLocal()
    try:
        logger.info("Checking for due schedules...")

        now_utc = datetime.now(timezone.utc)
        active_schedules = db.query(Schedule).filter(
            (Schedule.status == 'pending') | (Schedule.status == 'recurring')
        ).all()

        if not active_schedules:
            logger.info("No active schedules found.")
            return

        logger.info(f"Found {len(active_schedules)} active schedule(s) to evaluate.")

        for schedule in active_schedules:
            try:
                run_job = False
                # --- Logic for one-time jobs ---
                if schedule.status == 'pending':
                    if now_utc >= schedule.scheduled_time.replace(tzinfo=timezone.utc):
                        logger.info(f"One-time job {schedule.id} is due.")
                        run_job = True

                # --- Logic for recurring jobs ---
                elif schedule.status == 'recurring':
                    user_timezone_str = os.getenv('TIMEZONE', 'UTC')
                    user_timezone = pytz.timezone(user_timezone_str)
                    now_in_user_tz = datetime.now(user_timezone)

                    if now_in_user_tz.hour == schedule.hour and now_in_user_tz.minute == schedule.minute:
                        if schedule.last_run_at is None or schedule.last_run_at.astimezone(user_timezone).date() < now_in_user_tz.date():
                            logger.info(f"Recurring job {schedule.id} is due.")
                            run_job = True

                if run_job:
                    success = await execute_upload_logic(db, schedule)

                    if success:
                        if schedule.status == 'pending':
                            schedule.status = 'completed'
                            logger.info(f"Marking one-time job {schedule.id} as completed.")
                        elif schedule.status == 'recurring':
                            schedule.last_run_at = now_utc
                            if schedule.use_day_counter:
                                schedule.day_counter += 1
                            logger.info(f"Recurring job {schedule.id} ran successfully. Updating last_run_at and day_counter.")
                    else:
                        schedule.status = 'failed'
                        schedule.error_message = "Upload logic returned failure."
                        logger.error(f"Marking job {schedule.id} as failed.")

                    db.commit()

            except Exception as e:
                logger.error(f"Error processing schedule {schedule.id}: {e}", exc_info=True)
                db.rollback()

    finally:
        db.close()


async def main():
    """
    Main function to start the scheduler service loop.
    """
    logger.info("--- Starting Custom Scheduler Service ---")

    try:
        while True:
            await check_and_run_schedules()
            logger.info("Scheduler service sleeping for 60 seconds...")
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler service shutting down.")

if __name__ == "__main__":
    asyncio.run(main())
