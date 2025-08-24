from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import uvicorn
from pathlib import Path
import os
from datetime import datetime
from database import engine, SessionLocal, Base, init_database, get_db
from models import Content, Schedule, Account
from automation import ContentUploader
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import aiofiles
from typing import List

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Daily Content Uploader", 
    version="1.0.0",
    debug=os.getenv("DEBUG", "false").lower() == "true"
)

# CORS middleware
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_database()

# Setup directories
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
STATIC_FOLDER = "./static"
TEMPLATES_FOLDER = "./templates"

# Create directories if they don't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(STATIC_FOLDER).mkdir(exist_ok=True)
Path(TEMPLATES_FOLDER).mkdir(exist_ok=True)

# Setup static files and templates
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
templates = Jinja2Templates(directory=TEMPLATES_FOLDER)

# File upload settings
# Parse MAX_FILE_SIZE with unit support (e.g., "100MB", "50MB")
def parse_file_size(size_str):
    """Parse file size string like '100MB' to bytes"""
    if not size_str:
        return 104857600  # 100MB default
    
    size_str = size_str.upper().strip()
    
    # If it's already a number, return as int
    if size_str.isdigit():
        return int(size_str)
    
    # Parse size with unit
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    
    for unit in units:
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * units[unit])
            except ValueError:
                break
    
    # Fallback to default if parsing fails
    return 104857600  # 100MB default

MAX_FILE_SIZE = parse_file_size(os.getenv("MAX_FILE_SIZE", "100MB"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,mp4,mov,avi").split(",")

# Initialize content uploader
uploader = ContentUploader()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Daily Content Uploader...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'Not configured')}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Daily Content Uploader...")
    await uploader.close_browser()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard utama untuk mengelola konten"""
    try:
        contents = db.query(Content).order_by(Content.created_at.desc()).limit(10).all()
        schedules = db.query(Schedule).filter(Schedule.status == "pending").all()
        
        # Statistics
        total_contents = db.query(Content).count()
        pending_schedules = db.query(Schedule).filter(Schedule.status == "pending").count()
        published_contents = db.query(Content).filter(Content.status == "published").count()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "contents": contents,
            "schedules": schedules,
            "stats": {
                "total_contents": total_contents,
                "pending_schedules": pending_schedules,
                "published_contents": published_contents
            }
        })
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    if not file.filename:
        return False
    
    # Check file extension
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    return True

@app.post("/upload")
async def upload_content(
    file: UploadFile = File(...),
    caption: str = Form(...),
    platform: str = Form(...),
    schedule_time: str = Form(None),
    db: Session = Depends(get_db)
):
    """Upload konten baru"""
    try:
        # Validate file
        if not validate_file(file):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Save to database
        new_content = Content(
            filename=file.filename,
            file_path=file_path,
            caption=caption,
            platform=platform,
            file_type=file.content_type,
            file_size=file_size,
            status="uploaded"
        )
        db.add(new_content)
        db.commit()
        db.refresh(new_content)
        
        # Create schedule if provided
        if schedule_time:
            try:
                schedule_dt = datetime.fromisoformat(schedule_time)
                new_schedule = Schedule(
                    content_id=new_content.id,
                    platform=platform,
                    scheduled_time=schedule_dt,
                    status="pending"
                )
                db.add(new_schedule)
                db.commit()
            except ValueError:
                logger.warning(f"Invalid schedule time format: {schedule_time}")
        
        logger.info(f"Content uploaded successfully: {new_content.id}")
        return {"message": "Konten berhasil diupload", "content_id": new_content.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/publish/{content_id}")
async def publish_content(content_id: int, platform: str, db: Session = Depends(get_db)):
    """Publish konten langsung ke platform"""
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Konten tidak ditemukan")
        
        # Check if file exists
        if not os.path.exists(content.file_path):
            raise HTTPException(status_code=404, detail="File konten tidak ditemukan")
        
        # Upload using automation
        success = await uploader.upload_to_platform(content, platform)
        
        if success:
            content.status = "published"
            db.commit()
            logger.info(f"Content {content_id} published successfully to {platform}")
            return {"message": f"Konten berhasil dipublish ke {platform}"}
        else:
            content.status = "failed"
            db.commit()
            logger.error(f"Failed to publish content {content_id} to {platform}")
            raise HTTPException(status_code=500, detail="Gagal publish konten")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/schedules")
async def get_schedules(db: Session = Depends(get_db)):
    """Get semua jadwal yang pending"""
    try:
        schedules = db.query(Schedule).filter(Schedule.status == "pending").all()
        return {"schedules": [
            {
                "id": s.id,
                "content_id": s.content_id,
                "platform": s.platform,
                "scheduled_time": s.scheduled_time.isoformat(),
                "status": s.status,
                "retry_count": s.retry_count
            } for s in schedules
        ]}
    except Exception as e:
        logger.error(f"Error getting schedules: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/content/{content_id}")
async def delete_content(content_id: int, db: Session = Depends(get_db)):
    """Hapus konten"""
    try:
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(status_code=404, detail="Konten tidak ditemukan")
        
        # Delete file
        if os.path.exists(content.file_path):
            try:
                os.remove(content.file_path)
            except OSError as e:
                logger.warning(f"Could not delete file {content.file_path}: {e}")
        
        # Delete from database (schedules will be deleted automatically due to CASCADE)
        db.delete(content)
        db.commit()
        
        logger.info(f"Content {content_id} deleted successfully")
        return {"message": "Konten berhasil dihapus"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content {content_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/contents")
async def get_contents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all contents with pagination"""
    try:
        contents = db.query(Content).offset(skip).limit(limit).all()
        return {"contents": [
            {
                "id": c.id,
                "filename": c.filename,
                "platform": c.platform,
                "status": c.status,
                "file_size": c.file_size,
                "created_at": c.created_at.isoformat()
            } for c in contents
        ]}
    except Exception as e:
        logger.error(f"Error getting contents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload)
