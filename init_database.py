#!/usr/bin/env python3
"""
Database initialization script for production deployment
Run this script after setting up your MySQL database
"""
import os
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from database import init_database, SessionLocal
from models import Account
import getpass

def create_admin_account():
    """Create initial admin accounts for social media platforms"""
    db = SessionLocal()
    try:
        print("=== Setup Social Media Accounts ===")
        
        # Check if accounts already exist
        existing_accounts = db.query(Account).count()
        if existing_accounts > 0:
            print(f"Found {existing_accounts} existing accounts in database.")
            overwrite = input("Do you want to add more accounts? (y/n): ").lower()
            if overwrite != 'y':
                return
        
        platforms = ['instagram', 'tiktok']
        
        for platform in platforms:
            print(f"\n--- Setup {platform.title()} Account ---")
            add_account = input(f"Add {platform} account? (y/n): ").lower()
            
            if add_account == 'y':
                username = input(f"Enter {platform} username: ").strip()
                if not username:
                    print("Username cannot be empty. Skipping...")
                    continue
                
                password = getpass.getpass(f"Enter {platform} password: ")
                if not password:
                    print("Password cannot be empty. Skipping...")
                    continue
                
                # Check if account already exists
                existing = db.query(Account).filter(
                    Account.platform == platform,
                    Account.username == username
                ).first()
                
                if existing:
                    print(f"Account {username} for {platform} already exists. Skipping...")
                    continue
                
                # Create new account
                account = Account(
                    platform=platform,
                    username=username,
                    is_active=True
                )
                account.set_password(password)
                
                db.add(account)
                db.commit()
                
                print(f"✅ {platform.title()} account '{username}' added successfully!")
        
        print("\n=== Account Setup Complete ===")
        
    except Exception as e:
        print(f"Error creating accounts: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("=== Daily Content Uploader - Database Initialization ===")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check database configuration
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not configured in .env file")
        print("Please configure your MySQL database connection first.")
        return
    
    print(f"Database URL: {db_url}")
    
    try:
        # Initialize database tables
        print("\n1. Creating database tables...")
        init_database()
        print("✅ Database tables created successfully!")
        
        # Create upload directories
        print("\n2. Creating upload directories...")
        upload_folder = os.getenv('UPLOAD_FOLDER', './uploads')
        Path(upload_folder).mkdir(parents=True, exist_ok=True)
        Path('./static').mkdir(exist_ok=True)
        print("✅ Upload directories created!")
        
        # Setup accounts
        print("\n3. Setting up social media accounts...")
        create_admin_account()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Configure your web server (Apache)")
        print("2. Install Python dependencies: pip install -r requirements.txt")
        print("3. Install Playwright browsers: playwright install")
        print("4. Start the application")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
