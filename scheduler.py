import logging
from copy import deepcopy
from sqlalchemy.orm import Session

from models import Schedule, Content
from automation import ContentUploader

logger = logging.getLogger(__name__)

async def execute_upload_logic(db: Session, schedule: Schedule) -> bool:
    """
    This is the core logic that performs the upload for a given schedule.
    It uses the database session passed from the caller and returns True/False.
    It does NOT commit any changes to the database.
    """
    logger.info(f"--- Executing job for schedule_id: {schedule.id} ---")
    try:
        content_to_upload = db.query(Content).filter(Content.id == schedule.content_id).first()
        if not content_to_upload:
            logger.error(f"Execution failed: Content {schedule.content_id} not found for schedule {schedule.id}.")
            # The caller will handle the status update
            return False

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
            logger.info(f"✅ Upload successful for schedule {schedule.id}.")
            return True
        else:
            logger.error(f"❌ Upload process returned failure for schedule {schedule.id}.")
            return False

    except Exception as e:
        logging.error(f"An unexpected error in execute_upload_logic for schedule {schedule.id}: {e}", exc_info=True)
        return False
    finally:
        logger.info(f"--- Finished execution attempt for schedule_id: {schedule.id} ---")
