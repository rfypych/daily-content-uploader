import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from database import init_database, SessionLocal, engine
from models import Account, Base

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = Path("session.json")

# --- Functions ---

def setup_database_and_accounts(reset_db=False):
    """Initializes the database and creates the Instagram account entry if it doesn't exist."""
    logging.info("--- Langkah 1: Menyiapkan Database ---")
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logging.error("❌ DATABASE_URL tidak ditemukan di file .env. Silakan buat file .env dari .env.example.")
        return False

    try:
        if reset_db:
            logging.warning("⚠️ Flag --reset-db terdeteksi. Menghapus semua tabel dari database...")
            Base.metadata.drop_all(bind=engine)
            logging.info("✅ Semua tabel telah dihapus.")

        init_database()
        logging.info("✅ Database dan tabel berhasil dibuat.")

        db = SessionLocal()
        # Create Instagram account entry
        if INSTAGRAM_USERNAME:
            existing = db.query(Account).filter_by(platform="instagram", username=INSTAGRAM_USERNAME).first()
            if not existing:
                account = Account(platform="instagram", username=INSTAGRAM_USERNAME, is_active=True)
                if INSTAGRAM_PASSWORD:
                    account.set_password(INSTAGRAM_PASSWORD)
                db.add(account)
                db.commit()
                logging.info(f"✅ Akun '{INSTAGRAM_USERNAME}' ditambahkan ke database.")
            else:
                logging.info(f"✅ Akun '{INSTAGRAM_USERNAME}' sudah ada di database.")
        else:
            logging.warning("⚠️ INSTAGRAM_USERNAME tidak diatur di .env, tidak dapat menambahkan akun ke DB.")

        # Create Web App User
        WEB_USERNAME = os.getenv("WEB_USERNAME")
        WEB_PASSWORD = os.getenv("WEB_PASSWORD")
        if WEB_USERNAME and WEB_PASSWORD:
            web_user_exists = db.query(Account).filter_by(platform="webapp", username=WEB_USERNAME).first()
            if not web_user_exists:
                web_user = Account(platform="webapp", username=WEB_USERNAME)
                web_user.set_password(WEB_PASSWORD)
                db.add(web_user)
                db.commit()
                logging.info(f"✅ Akun web '{WEB_USERNAME}' berhasil dibuat. Gunakan ini untuk login ke dashboard.")
            else:
                logging.info(f"✅ Akun web '{WEB_USERNAME}' sudah ada.")
        else:
            logging.warning("⚠️ WEB_USERNAME atau WEB_PASSWORD tidak diatur di .env. Akun web tidak dibuat.")

        # Ensure upload folder exists
        upload_folder = os.getenv('UPLOAD_FOLDER', './uploads')
        Path(upload_folder).mkdir(parents=True, exist_ok=True)
        logging.info(f"✅ Folder upload '{upload_folder}' siap.")

        return True
    except Exception as e:
        logging.error(f"❌ Gagal menyiapkan database: {e}")
        return False
    finally:
        db.close()


def perform_interactive_login():
    """Performs the first-time interactive login to generate a session file."""
    logging.info("\n--- Langkah 2: Login Interaktif ke Instagram ---")

    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD]):
        logging.error("❌ INSTAGRAM_USERNAME atau INSTAGRAM_PASSWORD tidak ditemukan di file .env.")
        return

    if SESSION_FILE.exists():
        logging.warning(f"⚠️ File '{SESSION_FILE}' sudah ada.")
        overwrite = input("   Apakah Anda ingin login ulang dan menimpanya? (y/n): ").lower()
        if overwrite != 'y':
            logging.info("Login dibatalkan.")
            return

    cl = Client()

    def challenge_code_handler(username, choice):
        """Handles the 2FA challenge by asking the user for the code."""
        while True:
            try:
                code = input(f"\n>>> Masukkan kode 6 digit yang dikirim ke email Anda untuk akun '{username}': ").strip()
                if len(code) == 6 and code.isdigit():
                    return code
                else:
                    print("   [Error] Kode tidak valid. Harap masukkan 6 digit angka.")
            except (KeyboardInterrupt, EOFError):
                print("\nLogin dibatalkan.")
                return None

    cl.challenge_code_handler = challenge_code_handler

    try:
        logging.info(f"Mencoba login sebagai {INSTAGRAM_USERNAME}...")
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        logging.info(f"✅ Login berhasil! Sesi disimpan di '{SESSION_FILE}'.")
        logging.info("✅ Anda sekarang dapat menjalankan server utama dengan 'python3 main.py'.")
    except Exception as e:
        logging.error(f"❌ Gagal login: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    print("=====================================================")
    print("  Setup Aplikasi Daily Content Uploader  ")
    print("=====================================================")
    print("Skrip ini akan menyiapkan database dan memandu Anda")
    print("untuk login pertama kali ke Instagram.")
    print("-----------------------------------------------------")

    # Check for --reset-db flag
    reset_db_flag = "--reset-db" in sys.argv

    if setup_database_and_accounts(reset_db=reset_db_flag):
        # Only perform login if the DB setup was successful
        if not reset_db_flag:
             # Don't ask for login again if user is just resetting the DB
             # They should run separately if they want to do both.
            perform_interactive_login()
        else:
            logging.info("Database telah di-reset. Jalankan skrip lagi tanpa flag --reset-db untuk login.")

    print("\nProses setup selesai.")
