import logging
from copy import deepcopy

from models import Schedule, Content
from automation import ContentUploader

logger = logging.getLogger(__name__)


async def execute_upload_logic(schedule: Schedule, content_to_upload: Content) -> bool:
    """
    This is the core logic that performs the upload for a given schedule.
    It does NOT interact with the database. It returns True on success, False on failure.
    """
    logger.info(f"--- Executing job for schedule_id: {schedule.id} ---")
    try:
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
        else:
            logger.error(f"❌ Failed to upload content for schedule {schedule.id}. The uploader returned a non-success status.")

        return success

    except Exception as e:
        logging.error(f"An unexpected error in execute_upload_logic for schedule {schedule.id}: {e}", exc_info=True)
        return False
    finally:
        # The session is managed by the caller, so we don't close it here.
        logger.info(f"--- Finished execution for schedule_id: {schedule.id} ---")
