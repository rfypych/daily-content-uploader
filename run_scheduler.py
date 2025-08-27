import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from scheduler import scheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    Main function to start and run the scheduler indefinitely.
    This should be run as a separate, persistent process in production.
    """
    logger.info("Starting the standalone scheduler process...")
    try:
        await scheduler.start()
        # Keep the process alive
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, the scheduler runs on its own thread.
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler process stopped.")
    finally:
        await scheduler.stop()

if __name__ == "__main__":
    asyncio.run(main())
