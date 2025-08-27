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

logger = logging.getLogger(__name__)

# --- Standalone Job Execution Functions ---

async def execute_upload(schedule_id: int):
    """
    The function executed by the scheduler. It fetches job details from the DB
    and triggers the uploader. This is a standalone function to avoid serialization issues.
    """
    logger.info(f"--- Executing scheduled job for schedule_id: {schedule_id} ---")
    db = SessionLocal()
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            logger.error(f"Execution failed: Schedule {schedule_id} not found.")
            return

        if schedule.status != 'pending':
            logger.warning(f"Skipping job for schedule {schedule_id}: status is '{schedule.status}'.")
            return

        content = db.query(Content).filter(Content.id == schedule.content_id).first()
        if not content:
            logger.error(f"Execution failed: Content {schedule.content_id} not found.")
            schedule.status = "failed"
            schedule.error_message = "Content not found"
            db.commit()
            return

        logger.info(f"Found content '{content.filename}'. Starting upload to {content.platform}...")
        uploader = ContentUploader()
        success = await uploader.upload_to_platform(content, content.platform)

        if success:
            schedule.status = "completed"
            content.status = "published"
            logger.info(f"✅ Successfully uploaded content {content.id} via schedule {schedule_id}.")
        else:
            schedule.status = "failed"
            schedule.error_message = "Upload process returned failure."
            logger.error(f"❌ Failed to upload content {content.id} via schedule {schedule_id}.")

        db.commit()

    except Exception as e:
        logging.error(f"An unexpected error occurred in execute_upload for schedule {schedule_id}: {e}", exc_info=True)
        # Re-fetch schedule to write error status
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if schedule:
            schedule.status = "failed"
            schedule.error_message = str(e)
            db.commit()
    finally:
        db.close()
        logger.info(f"--- Finished execution for schedule_id: {schedule_id} ---")

async def execute_upload_by_content_id(content_id: int, platform: str):
    """A wrapper for daily jobs to create a new schedule entry each time."""
    db = SessionLocal()
    try:
        new_schedule = Schedule(content_id=content_id, platform=platform, scheduled_time=datetime.utcnow(), status="pending")
        db.add(new_schedule)
        db.commit()
        logging.info(f"Daily job triggered: Created new schedule entry {new_schedule.id} for content {content_id}.")
        await execute_upload(new_schedule.id)
    except Exception as e:
        logging.error(f"Failed to create daily schedule entry for content {content_id}: {e}")
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
            func=execute_upload, # Use the standalone function
            trigger=DateTrigger(run_date=schedule.scheduled_time),
            args=[schedule.id],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled job '{job_id}' for content {schedule.content_id} at {schedule.scheduled_time}")
            
    async def add_daily_schedule(self, content_id: int, platform: str, hour: int, minute: int):
        """Adds a daily recurring job."""
        job_id = f"daily_{content_id}_{platform}"
        self.scheduler.add_job(
            func=execute_upload_by_content_id, # Use the standalone function
            trigger=CronTrigger(hour=hour, minute=minute, timezone='UTC'),
            args=[content_id, platform],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Added daily recurring job '{job_id}' for content {content_id} at {hour:02d}:{minute:02d} UTC.")

# --- Global Instance ---
scheduler = ContentScheduler()
