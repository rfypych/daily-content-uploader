from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import asyncio
import logging
from database import SessionLocal
from models import Schedule, Content
from automation import ContentUploader

logger = logging.getLogger(__name__)

class ContentScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.uploader = ContentUploader()
        
    async def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Content scheduler started")
        
        # Check for pending schedules on startup
        await self.check_pending_schedules()
        
    async def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        await self.uploader.close_browser()
        logger.info("Content scheduler stopped")
        
    async def check_pending_schedules(self):
        """Check and schedule pending uploads"""
        db = SessionLocal()
        try:
            pending_schedules = db.query(Schedule).filter(
                Schedule.status == "pending",
                Schedule.scheduled_time > datetime.utcnow()
            ).all()
            
            for schedule in pending_schedules:
                await self.schedule_upload(schedule)
                
        finally:
            db.close()
            
    async def schedule_upload(self, schedule: Schedule):
        """Schedule a single upload"""
        job_id = f"upload_{schedule.id}"
        
        # Remove existing job if exists
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            
        # Schedule new job
        self.scheduler.add_job(
            self.execute_upload,
            DateTrigger(run_date=schedule.scheduled_time),
            args=[schedule.id],
            id=job_id,
            replace_existing=True
        )
        
        logger.info(f"Scheduled upload {schedule.id} for {schedule.scheduled_time}")
        
    async def execute_upload(self, schedule_id: int):
        """Execute scheduled upload"""
        db = SessionLocal()
        try:
            schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if not schedule:
                logger.error(f"Schedule {schedule_id} not found")
                return
                
            content = db.query(Content).filter(Content.id == schedule.content_id).first()
            if not content:
                logger.error(f"Content {schedule.content_id} not found")
                schedule.status = "failed"
                schedule.error_message = "Content not found"
                db.commit()
                return
            
            # Execute upload
            success = await self.uploader.upload_to_platform(content, schedule.platform)
            
            if success:
                schedule.status = "completed"
                content.status = "published"
                logger.info(f"Successfully uploaded content {content.id} to {schedule.platform}")
            else:
                schedule.status = "failed"
                schedule.error_message = "Upload failed"
                logger.error(f"Failed to upload content {content.id} to {schedule.platform}")
                
            db.commit()
            
        except Exception as e:
            logger.error(f"Error executing upload {schedule_id}: {str(e)}")
            schedule.status = "failed"
            schedule.error_message = str(e)
            db.commit()
        finally:
            db.close()
            
    async def add_daily_schedule(self, content_id: int, platform: str, hour: int, minute: int):
        """Add daily recurring schedule"""
        db = SessionLocal()
        try:
            # Create schedule record
            schedule = Schedule(
                content_id=content_id,
                platform=platform,
                scheduled_time=datetime.now().replace(hour=hour, minute=minute, second=0),
                status="recurring"
            )
            db.add(schedule)
            db.commit()
            
            # Add recurring job
            job_id = f"daily_{content_id}_{platform}"
            self.scheduler.add_job(
                self.execute_upload,
                CronTrigger(hour=hour, minute=minute),
                args=[schedule.id],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Added daily schedule for content {content_id} at {hour}:{minute}")
            
        finally:
            db.close()
            
    def get_scheduled_jobs(self):
        """Get all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs

# Global scheduler instance
scheduler = ContentScheduler()

async def start_scheduler():
    """Start the global scheduler"""
    await scheduler.start()

async def stop_scheduler():
    """Stop the global scheduler"""
    await scheduler.stop()

if __name__ == "__main__":
    async def main():
        await start_scheduler()
        try:
            # Keep running
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            await stop_scheduler()
    
    asyncio.run(main())
