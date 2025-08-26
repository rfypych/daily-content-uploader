import os
from pathlib import Path
from dotenv import load_dotenv
from database import init_database, SessionLocal
from models import Account
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_accounts_from_env():
    """
    Creates or updates social media accounts in the database using credentials
    from environment variables.
    """
    db = SessionLocal()
    try:
        logging.info("=== Setting up accounts from .env file ===")
        # We only set up Instagram now, TikTok logic is removed.
        accounts_to_create = [
            {"platform": "instagram", "username_var": "INSTAGRAM_USERNAME", "password_var": "INSTAGRAM_PASSWORD"},
        ]

        for acc_info in accounts_to_create:
            username = os.getenv(acc_info["username_var"])
            password = os.getenv(acc_info["password_var"])
            platform = acc_info["platform"]

            if not all([username, password]):
                logging.warning(f"Skipping {platform}: credentials not fully set in .env")
                continue

            existing = db.query(Account).filter_by(platform=platform, username=username).first()
            if existing:
                logging.info(f"Account for {username} on {platform} already exists. Skipping.")
                continue

            account = Account(platform=platform, username=username, is_active=True)
            account.set_password(password)
            db.add(account)
            db.commit()
            logging.info(f"✅ {platform.title()} account '{username}' created successfully!")

    except Exception as e:
        logging.error(f"An error occurred during account creation: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logging.info("=== Non-Interactive Database and Account Setup ===")
    load_dotenv()

    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logging.error("❌ DATABASE_URL not configured in .env file")
    else:
        logging.info(f"Database URL: {db_url}")
        logging.info("1. Creating database tables...")
        init_database()
        logging.info("✅ Tables created.")

        logging.info("\n2. Creating accounts from .env...")
        create_accounts_from_env()
        logging.info("✅ Account setup complete.")

    # Also create the upload directory if it doesn't exist
    upload_folder = os.getenv('UPLOAD_FOLDER', './uploads')
    Path(upload_folder).mkdir(parents=True, exist_ok=True)
    logging.info(f"✅ Upload directory '{upload_folder}' ensured.")

    logging.info("\n🎉 Setup finished successfully.")
