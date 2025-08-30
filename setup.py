import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client

from database import init_database, SessionLocal, engine
from models import Account, Base
from auth import get_password_hash

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
load_dotenv()

SESSION_FILE = Path("session.json")

# --- Functions ---

def setup_database_and_accounts(reset_db=False):
    """Initializes the database and creates necessary accounts."""
    logging.info("--- Step 1: Setting up Database ---")
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logging.error("❌ DATABASE_URL not found in .env file. Please create one from .env.example.")
        return False

    try:
        if reset_db:
            logging.warning("⚠️ --reset-db flag detected. Dropping all tables from the database...")
            Base.metadata.drop_all(bind=engine)
            logging.info("✅ All tables have been dropped.")

        init_database()
        logging.info("✅ Database and tables created successfully.")

        db = SessionLocal()

        # Create Web App User for dashboard login
        WEB_USERNAME = os.getenv("WEB_USERNAME")
        WEB_PASSWORD = os.getenv("WEB_PASSWORD")
        if WEB_USERNAME and WEB_PASSWORD:
            web_user_exists = db.query(Account).filter_by(platform="webapp", username=WEB_USERNAME).first()
            if not web_user_exists:
                hashed_password = get_password_hash(WEB_PASSWORD)
                web_user = Account(platform="webapp", username=WEB_USERNAME, password=hashed_password)
                db.add(web_user)
                db.commit()
                logging.info(f"✅ Web account '{WEB_USERNAME}' created. Use this to log in to the dashboard.")
            else:
                logging.info(f"✅ Web account '{WEB_USERNAME}' already exists.")
        else:
            logging.warning("⚠️ WEB_USERNAME or WEB_PASSWORD not set in .env. Web user account not created.")

        # Ensure upload folder exists
        upload_folder = os.getenv('UPLOAD_FOLDER', './uploads')
        Path(upload_folder).mkdir(parents=True, exist_ok=True)
        logging.info(f"✅ Upload folder '{upload_folder}' is ready.")

        return True
    except Exception as e:
        logging.error(f"❌ Failed to set up database: {e}")
        return False
    finally:
        db.close()

def perform_interactive_login():
    """
    Performs the first-time interactive login on a LOCAL machine
    to generate a session file that can be uploaded to the server.
    """
    logging.info("\n--- Step 2: Interactive Instagram Login (Local Machine) ---")
    logging.info("This step will generate a 'session.json' file to let your server securely access Instagram without using a password.")

    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logging.error("❌ INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD not found in your .env file.")
        return

    if SESSION_FILE.exists():
        logging.warning(f"⚠️ An existing '{SESSION_FILE}' was found.")
        overwrite = input("   Do you want to log in again and overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            logging.info("Login cancelled.")
            return

    cl = Client()

    def challenge_code_handler(username, choice):
        while True:
            try:
                code = input(f"\n>>> Enter the 6-digit code sent to your email for account '{username}': ").strip()
                if len(code) == 6 and code.isdigit():
                    return code
                else:
                    print("   [Error] Invalid code. Please enter 6 digits.")
            except (KeyboardInterrupt, EOFError):
                print("\nLogin cancelled by user.")
                return None

    cl.challenge_code_handler = challenge_code_handler

    try:
        logging.info(f"Attempting to log in as {INSTAGRAM_USERNAME}...")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        logging.info("✅ Login successful!")
        logging.info(f"✅ Session saved to '{SESSION_FILE}'.")
        print("\n=====================================================")
        print("IMPORTANT: Upload the 'session.json' file to your server in the same directory as the application.")
        print("=====================================================")
    except Exception as e:
        logging.error(f"❌ Login failed: {e}")
        logging.error("   This can happen due to an incorrect password, or Instagram's security measures.")
        logging.error("   Try logging in manually from your phone first to ensure the account is active.")

# --- Main Execution ---

if __name__ == "__main__":
    print("=====================================================")
    print("  Application Setup & Session Generator")
    print("=====================================================")
    print("This script prepares the database and guides you through")
    print("the first-time Instagram login to create 'session.json'.")
    print("It is recommended to run this script on your LOCAL computer.")
    print("-----------------------------------------------------")

    reset_db_flag = "--reset-db" in sys.argv

    if setup_database_and_accounts(reset_db=reset_db_flag):
        if not reset_db_flag:
            perform_interactive_login()
        else:
            logging.info("Database has been reset. Run the script again without the --reset-db flag to log in.")

    print("\nSetup process finished.")
