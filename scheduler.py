import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import logging
from database import SessionLocal
from models import Schedule, Content
from automation import ContentUploader
from copy import deepcopy

logger = logging.getLogger(__name__)

# --- Standalone Job Execution Functions ---

async def execute_scheduled_upload(schedule_id: int):
    """
    The function executed by the scheduler for one-time jobs.
    """
    logger.info(f"--- Executing one-time job for schedule_id: {schedule_id} ---")
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule or schedule.status != 'pending':
            logger.warning(f"Skipping job for schedule {schedule_id}: not found or status is not 'pending'.")
            return

        content = db.query(Content).filter(Content.id == schedule.content_id).first()
        if not content:
            logger.error(f"Execution failed: Content {schedule.content_id} not found.")
            schedule.status = "failed"; schedule.error_message = "Content not found"; db.commit()
            return

        logger.info(f"Found content '{content.filename}'. Starting upload to {content.platform}...")
        uploader = ContentUploader()
        success = await uploader.upload_to_platform(content, content.platform)

        if success:
            schedule.status = "completed"; content.status = "published"
            logger.info(f"✅ Successfully uploaded content {content.id} via schedule {schedule_id}.")
        else:
            schedule.status = "failed"; schedule.error_message = "Upload process returned failure."
            logger.error(f"❌ Failed to upload content {content.id} via schedule {schedule_id}.")
        db.commit()

    except Exception as e:
        logging.error(f"An unexpected error in execute_scheduled_upload for schedule {schedule_id}: {e}", exc_info=True)
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.status = "failed"; schedule.error_message = str(e); db.commit()
    finally:
        db.close()
        logger.info(f"--- Finished execution for schedule_id: {schedule_id} ---")

async def execute_recurring_job(recurring_schedule_id: int):
    """
    The function executed by the cron scheduler for daily jobs.
    It handles the dynamic caption logic.
    """
    logger.info(f"--- Executing recurring job for master schedule_id: {recurring_schedule_id} ---")
    db = SessionLocal()
    try:
        master_schedule = db.query(Schedule).filter(Schedule.id == recurring_schedule_id).first()
        if not master_schedule or master_schedule.status != 'recurring':
            logger.error(f"Master recurring schedule {recurring_schedule_id} not found or inactive. Removing job.")
            scheduler.scheduler.remove_job(f"daily_{recurring_schedule_id}")
            return

        content_to_upload = db.query(Content).filter(Content.id == master_schedule.content_id).first()
        if not content_to_upload:
            logger.error(f"Content {master_schedule.content_id} for recurring schedule {recurring_schedule_id} not found.")
            return

        # Create a deepcopy to modify the caption without changing the original DB entry
        content_for_this_run = deepcopy(content_to_upload)

        # Handle dynamic caption
        if master_schedule.use_day_counter:
            day = master_schedule.day_counter
            original_caption = content_to_upload.caption or ""
            content_for_this_run.caption = f"Day {day} - {original_caption}"
            logger.info(f"Applying dynamic caption: '{content_for_this_run.caption}'")

        uploader = ContentUploader()
        success = await uploader.upload_to_platform(content_for_this_run, master_schedule.platform)

        if success:
            logger.info(f"✅ Successfully uploaded content for recurring schedule {recurring_schedule_id}.")
            if master_schedule.use_day_counter:
                master_schedule.day_counter += 1
                logger.info(f"Incremented day counter for schedule {recurring_schedule_id} to {master_schedule.day_counter}.")
            db.commit()
        else:
            logger.error(f"❌ Failed to upload content for recurring schedule {recurring_schedule_id}.")

    except Exception as e:
        logging.error(f"An unexpected error in execute_recurring_job for schedule {recurring_schedule_id}: {e}", exc_info=True)
    finally:
        db.close()

# --- Scheduler Class ---

class ContentScheduler:
    def __init__(self):
        jobstores = {'default': SQLAlchemyJobStore(url=os.getenv("DATABASE_URL", "sqlite:///./daily_content.db"))}
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        
    async def start(self):
        self.scheduler.start()
        logger.info("Content scheduler started with SQLAlchemyJobStore.")
        
    async def stop(self):
        self.scheduler.shutdown()
        logger.info("Content scheduler stopped.")
        
    async def schedule_upload(self, schedule: Schedule):
        """Schedules a one-time upload."""
        job_id = f"upload_{schedule.id}"
        self.scheduler.add_job(
            func=execute_scheduled_upload,
            trigger=DateTrigger(run_date=schedule.scheduled_time),
            args=[schedule.id],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled one-time job '{job_id}' for content {schedule.content_id} at {schedule.scheduled_time}")
            
    async def add_daily_schedule(self, content_id: int, platform: str, hour: int, minute: int, use_day_counter: bool):
        """Adds a daily recurring job."""
        db = SessionLocal()
        try:
            # Create a master schedule entry to track the recurring job
            new_recurring_schedule = Schedule(
                content_id=content_id,
                platform=platform,
                scheduled_time=datetime.utcnow(), # Not relevant for cron, but required
                status="recurring",
                use_day_counter=use_day_counter
            )
            db.add(new_recurring_schedule)
            db.commit()

            job_id = f"daily_{new_recurring_schedule.id}"
            self.scheduler.add_job(
                func=execute_recurring_job,
                trigger=CronTrigger(hour=hour, minute=minute, timezone='UTC'),
                args=[new_recurring_schedule.id], # Pass the ID of the recurring schedule
                id=job_id,
                replace_existing=True
            )
            logger.info(f"Added daily recurring job '{job_id}' for content {content_id} at {hour:02d}:{minute:02d} UTC.")
        finally:
            db.close()

# --- Global Instance ---
scheduler = ContentScheduler()
