import logging
from copy import deepcopy

from database import SessionLocal
from models import Schedule, Content
from automation import ContentUploader

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session

async def execute_upload_logic(db: Session, schedule: Schedule):
    """
    This is the core logic that performs the upload for a given schedule.
    It uses the database session passed from the caller.
    """
    logger.info(f"--- Executing job for schedule_id: {schedule.id} ---")
    try:
        # The schedule object is already in the session from the caller.
        content_to_upload = db.query(Content).filter(Content.id == schedule.content_id).first()
        if not content_to_upload:
            logger.error(f"Execution failed: Content {schedule.content_id} not found for schedule {schedule.id}.")
            schedule.status = "failed"
            schedule.error_message = "Content not found"
            db.commit()
            return

        # For recurring jobs with a day counter, we create a temporary copy
        # of the content to modify its caption.
        if schedule.status == 'recurring' and schedule.use_day_counter:
            content_for_this_run = deepcopy(content_to_upload)
            day = schedule.day_counter
            original_caption = content_to_upload.caption or ""
            content_for_this_run.caption = f"Day {day} {original_caption}"
            logger.info(f"Applying dynamic caption for recurring job: '{content_for_this_run.caption}'")
        else:
            content_for_this_run = content_to_upload

        logger.info(f"Found content '{content_for_this_run.filename}'. Starting upload to {schedule.platform}...")
        uploader = ContentUploader()
        success = await uploader.upload_to_platform(content_for_this_run, schedule.platform)

        if success:
            logger.info(f"✅ Successfully uploaded content for schedule {schedule.id}.")
            if schedule.status == 'pending':
                schedule.status = "completed"
                content_to_upload.status = "published"
            elif schedule.status == 'recurring':
                if schedule.use_day_counter:
                    schedule.day_counter += 1
                    logger.info(f"Incremented day counter for schedule {schedule.id} to {schedule.day_counter}.")
        else:
            schedule.status = "failed"
            schedule.error_message = "Upload process returned failure."
            logger.error(f"❌ Failed to upload content for schedule {schedule.id}.")

        db.commit()

    except Exception as e:
        logging.error(f"An unexpected error in execute_upload_logic for schedule {schedule.id}: {e}", exc_info=True)
        # Make sure to get a fresh object in the current session for update
        schedule_to_fail = db.query(Schedule).filter(Schedule.id == schedule.id).first()
        if schedule_to_fail:
            schedule_to_fail.status = "failed"
            schedule_to_fail.error_message = str(e)
            db.commit()
    finally:
        # The session is managed by the caller, so we don't close it here.
        logger.info(f"--- Finished execution for schedule_id: {schedule.id} ---")
