import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import asyncio
import logging
from database import SessionLocal
from models import Schedule, Content
from automation import ContentUploader

logger = logging.getLogger(__name__)

# --- Scheduler Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./daily_content.db")

jobstores = {
    'default': SQLAlchemyJobStore(url=DATABASE_URL)
}

class ContentScheduler:
    def __init__(self):
        # Initialize scheduler with the database job store
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self.uploader = ContentUploader()
        
    async def start(self):
        """Start the scheduler and load pending schedules from the DB."""
        self.scheduler.start()
        logger.info("Content scheduler started with SQLAlchemyJobStore.")
        
    async def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Content scheduler stopped.")
        
    async def schedule_upload(self, schedule: Schedule):
        """
        Schedule a single upload. The job is stored in the database.
        The job will call the execute_upload function with the schedule's ID.
        """
        job_id = f"upload_{schedule.id}"
        
        # Add the job. replace_existing=True ensures that if a job with the same ID
        # already exists, it will be replaced. This is useful for rescheduling.
        self.scheduler.add_job(
            func=self.execute_upload,
            trigger=DateTrigger(run_date=schedule.scheduled_time),
            args=[schedule.id],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled job '{job_id}' for content {schedule.content_id} at {schedule.scheduled_time}")
        
    async def execute_upload(self, schedule_id: int):
        """
        The function executed by the scheduler. It fetches the job details
        from the database and triggers the uploader.
        """
        logger.info(f"--- Executing scheduled job for schedule_id: {schedule_id} ---")
        db = SessionLocal()
        try:
            schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if not schedule:
                logger.error(f"Execution failed: Schedule {schedule_id} not found in database.")
                return

            if schedule.status != 'pending':
                logger.warning(f"Skipping job for schedule {schedule_id}: status is '{schedule.status}', not 'pending'.")
                return
                
            content = db.query(Content).filter(Content.id == schedule.content_id).first()
            if not content:
                logger.error(f"Execution failed: Content {schedule.content_id} for schedule {schedule_id} not found.")
                schedule.status = "failed"
                schedule.error_message = "Content not found"
                db.commit()
                return
            
            logger.info(f"Found content '{content.filename}' for schedule {schedule_id}. Starting upload to {content.platform}...")
            # The uploader object is created on the fly by the scheduler in the worker process
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
            # Ensure DB session is active before trying to write the error
            if db.is_active:
                try:
                    # Re-fetch schedule in case session was invalidated
                    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
                    if schedule:
                        schedule.status = "failed"
                        schedule.error_message = str(e)
                        db.commit()
                except Exception as db_err:
                    logging.error(f"Failed to write error status to DB for schedule {schedule_id}: {db_err}")
        finally:
            db.close()
            logger.info(f"--- Finished execution for schedule_id: {schedule_id} ---")
            
    async def add_daily_schedule(self, content_id: int, platform: str, hour: int, minute: int):
        """Add daily recurring schedule."""
        job_id = f"daily_{content_id}_{platform}"

        self.scheduler.add_job(
            self.execute_upload_by_content_id, # Use a wrapper to find the latest schedule
            CronTrigger(hour=hour, minute=minute, timezone='UTC'),
            args=[content_id, platform],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Added daily recurring job '{job_id}' for content {content_id} at {hour:02d}:{minute:02d} UTC.")

    async def execute_upload_by_content_id(self, content_id: int, platform: str):
        """A wrapper for daily jobs to create a new schedule entry each time."""
        db = SessionLocal()
        try:
            # Create a new one-time schedule entry for this daily execution
            new_schedule = Schedule(
                content_id=content_id,
                platform=platform,
                scheduled_time=datetime.utcnow(),
                status="pending"
            )
            db.add(new_schedule)
            db.commit()
            logging.info(f"Daily job triggered: Created new schedule entry with ID {new_schedule.id} for content {content_id}.")
            # Execute the upload for the newly created schedule
            await self.execute_upload(new_schedule.id)
        except Exception as e:
            logging.error(f"Failed to create daily schedule entry for content {content_id}: {e}")
        finally:
            db.close()

# Global scheduler instance
scheduler = ContentScheduler()
