import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add project root to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db
from models import Base, Content

# Use a separate in-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency override for tests
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

import main
import auth

app.dependency_overrides[get_db] = override_get_db

# Mock authentication
def override_get_current_user():
    return {"username": "testuser"}

app.dependency_overrides[auth.get_current_user] = override_get_current_user


class TestContentDeletion(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

        # Create a mock upload folder
        self.upload_folder = Path("./test_uploads")
        self.upload_folder.mkdir(exist_ok=True)

        # Override UPLOAD_FOLDER in main
        main.UPLOAD_FOLDER = str(self.upload_folder)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

        # Clean up mock upload folder
        for f in self.upload_folder.glob("*"):
            f.unlink()
        self.upload_folder.rmdir()

    def test_delete_album_content_deletes_all_files(self):
        """
        Verify that deleting a content item with multiple file paths (an album)
        successfully deletes all associated files from the filesystem.
        """
        # 1. Create dummy files
        file1_path = self.upload_folder / "test_image_1.jpg"
        file2_path = self.upload_folder / "test_image_2.jpg"

        file1_path.touch()
        file2_path.touch()

        self.assertTrue(file1_path.exists())
        self.assertTrue(file2_path.exists())

        # 2. Create a mock Content object in the database
        album_file_paths = f"{file1_path},{file2_path}"

        new_content = Content(
            filename="Test Album",
            file_path=album_file_paths,
            caption="Test caption",
            post_type="album"
        )
        self.db.add(new_content)
        self.db.commit()
        self.db.refresh(new_content)
        content_id = new_content.id

        # 3. Call the delete endpoint
        response = self.client.delete(f"/content/{content_id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Content and associated files deleted successfully")

        # 4. Assert that the content is deleted from the database
        deleted_content = self.db.query(Content).filter(Content.id == content_id).first()
        self.assertIsNone(deleted_content)

        # 5. Assert that the files are deleted from the filesystem
        self.assertFalse(file1_path.exists(), "File 1 should have been deleted")
        self.assertFalse(file2_path.exists(), "File 2 should have been deleted")

if __name__ == '__main__':
    unittest.main()
