import asyncio
import logging
import os
import pytz
from dotenv import load_dotenv
from datetime import datetime, timezone, time

# Load environment variables first
load_dotenv()

from scheduler import execute_upload_logic
from database import SessionLocal
from models import Schedule, Content

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_and_run_schedules():
    """
    The core function of the custom scheduler.
    - Fetches all active schedules (`pending` or `recurring`).
    - Checks if they are due to be run.
    - Executes them if they are.
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
                    # Compare timezone-aware and naive datetimes correctly
                    if now_utc >= schedule.scheduled_time.replace(tzinfo=timezone.utc):
                        logger.info(f"One-time job {schedule.id} is due (scheduled for {schedule.scheduled_time}).")
                        run_job = True

                # --- Logic for recurring jobs ---
                elif schedule.status == 'recurring':
                    user_timezone_str = os.getenv('TIMEZONE', 'UTC')
                    user_timezone = pytz.timezone(user_timezone_str)
                    now_in_user_tz = datetime.now(user_timezone)

                    # Check if it's the right time of day in the user's timezone
                    if now_in_user_tz.hour == schedule.hour and now_in_user_tz.minute == schedule.minute:
                        # Check if it has already run today (in the user's timezone)
                        if schedule.last_run_at is None or schedule.last_run_at.astimezone(user_timezone).date() < now_in_user_tz.date():
                            logger.info(f"Recurring job {schedule.id} is due (scheduled for {schedule.hour:02d}:{schedule.minute:02d} in {user_timezone_str}).")
                            run_job = True
                        else:
                            logger.info(f"Recurring job {schedule.id} has already run today at {schedule.last_run_at.astimezone(user_timezone)}.")

                if run_job:
                    logger.info(f"Preparing to execute job for schedule {schedule.id}...")
                    content = db.query(Content).filter(Content.id == schedule.content_id).first()

                    if not content:
                        logger.error(f"Execution failed: Content {schedule.content_id} not found for schedule {schedule.id}.")
                        schedule.status = "failed"
                        schedule.error_message = "Content not found"
                        db.commit()
                        continue

                    # Execute the upload logic, which is now DB-independent
                    success = await execute_upload_logic(schedule, content)

                    # Now, handle all database updates based on the result
                    if success:
                        if schedule.status == 'pending':
                            schedule.status = 'completed'
                            content.status = 'published'
                            logger.info(f"One-time job {schedule.id} completed successfully.")
                        elif schedule.status == 'recurring':
                            schedule.day_counter += 1
                            schedule.last_run_at = now_utc
                            logger.info(f"Recurring job {schedule.id} completed successfully. Day counter is now {schedule.day_counter}.")
                    else:
                        schedule.status = 'failed'
                        schedule.error_message = "Upload process failed. See logs for details."
                        logger.error(f"Job {schedule.id} failed during execution.")

                    db.commit()

            except Exception as e:
                logger.error(f"Error processing schedule {schedule.id}: {e}", exc_info=True)

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
