from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
import os
import logging
import uvicorn
from datetime import datetime, timezone
import shutil
import aiofiles
from contextlib import asynccontextmanager

from database import SessionLocal, engine, Base, init_database, get_db
from models import Content, Schedule, Account
from automation import ContentUploader
# Scheduler is now a separate service and not imported directly.

# Create database tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize content uploader
uploader = ContentUploader()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    logger.info("Starting Daily Content Uploader Web Server...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Database URL: {os.getenv('DATABASE_URL', 'Not configured')}")
    yield
    logger.info("Shutting down Daily Content Uploader Web Server...")

# FastAPI app with lifespan
app = FastAPI(
    title="Daily Content Uploader",
    description="Automated Instagram & TikTok Content Upload System",
    version="1.0.0",
    lifespan=lifespan
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

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(STATIC_FOLDER).mkdir(exist_ok=True)
Path(TEMPLATES_FOLDER).mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
templates = Jinja2Templates(directory=TEMPLATES_FOLDER)

def parse_file_size(size_str):
    if not size_str: return 104857600
    size_str = size_str.upper().strip()
    if size_str.isdigit(): return int(size_str)
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
    for unit in units:
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * units[unit])
            except ValueError: break
    return 104857600

MAX_FILE_SIZE = parse_file_size(os.getenv("MAX_FILE_SIZE", "100MB"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,mp4,mov,avi").split(",")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard to manage content."""
    try:
        contents = db.query(Content).order_by(Content.created_at.desc()).limit(10).all()
        schedules = db.query(Schedule).filter(Schedule.status == "pending").all()
        total_contents = db.query(Content).count()
        pending_schedules = db.query(Schedule).filter(Schedule.status == "pending").count()
        published_contents = db.query(Content).filter(Content.status == "published").count()
        recurring_schedules_q = db.query(Schedule).filter(Schedule.status == 'recurring').all()
        recurring_map = {s.content_id: s for s in recurring_schedules_q}

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "contents": contents,
            "schedules": schedules,
            "recurring_map": recurring_map,
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
    if not file.filename: return False
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS: return False
    return True

from typing import List

@app.post("/upload")
async def upload_content(
    files: List[UploadFile] = File(...),
    caption: str = Form(""),
    post_type: str = Form(...),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    total_size = 0
    file_paths = []
    primary_filename = files[0].filename
    primary_file_type = files[0].content_type

    for file in files:
        if not validate_file(file):
            raise HTTPException(status_code=400, detail=f"File type not allowed for {file.filename}")
        
        file_content = await file.read()
        file_size = len(file_content)
        total_size += file_size
        
        if total_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"Total file size exceeds limit of {MAX_FILE_SIZE / 1024**2}MB")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        file_paths.append(file_path)

    db_file_path = ",".join(file_paths)
    db_filename = f"Album of {len(files)} items" if post_type == "album" else primary_filename

    try:
        new_content = Content(
            filename=db_filename, file_path=db_file_path, caption=caption,
            platform="instagram", post_type=post_type, file_type=primary_file_type,
            file_size=total_size, status="uploaded"
        )
        db.add(new_content)
        db.commit()
        db.refresh(new_content)
        
        logger.info(f"Content entry created successfully: ID {new_content.id}, Type: {post_type}")
        return {"message": "Content uploaded and saved successfully.", "content_id": new_content.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/publish/{content_id}")
async def publish_content(content_id: int, platform: str, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if not os.path.exists(content.file_path):
        raise HTTPException(status_code=404, detail="Content file not found")

    success = await uploader.upload_to_platform(content, platform)

    if success:
        content.status = "published"
        db.commit()
        logger.info(f"Content {content_id} published successfully to {platform}")
        return {"message": f"Content published successfully to {platform}"}
    else:
        content.status = "failed"
        db.commit()
        logger.error(f"Failed to publish content {content_id} to {platform}")
        raise HTTPException(status_code=500, detail="Failed to publish content")

@app.get("/schedules")
async def get_schedules(db: Session = Depends(get_db)):
    """Get all pending schedules"""
    schedules = db.query(Schedule).filter(Schedule.status == "pending").all()
    return schedules

@app.delete("/content/{content_id}")
async def delete_content(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if os.path.exists(content.file_path):
        try:
            os.remove(content.file_path)
        except OSError as e:
            logger.warning(f"Could not delete file {content.file_path}: {e}")

    db.delete(content)
    db.commit()

    logger.info(f"Content {content_id} deleted successfully")
    return {"message": "Content deleted successfully"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/contents")
async def get_contents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all contents with pagination"""
    contents = db.query(Content).offset(skip).limit(limit).all()
    return {"contents": contents}

@app.post("/schedule/daily")
async def create_daily_schedule(request: dict, db: Session = Depends(get_db)):
    """Creates a daily recurring schedule intent."""
    content_id = request.get("content_id")
    platform = request.get("platform")
    time_str = request.get("time")

    if not all([content_id, platform, time_str]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        hour, minute = map(int, time_str.split(":"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM.")

    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    use_day_counter = request.get("use_day_counter", False)
    start_day = request.get("start_day", 1)

    new_schedule = Schedule(
        content_id=content_id, platform=platform, status="recurring",
        use_day_counter=use_day_counter, hour=hour, minute=minute,
        day_counter=int(start_day),
        scheduled_time=datetime.now(timezone.utc)
    )
    db.add(new_schedule)
    db.commit()

    logger.info(f"Daily schedule intent for content {content_id} created successfully.")
    return {"message": "Daily schedule intent created. The scheduler will pick it up shortly."}

@app.post("/schedule/once")
async def create_one_time_schedule(request: dict, db: Session = Depends(get_db)):
    """Creates a one-time schedule intent."""
    content_id = request.get("content_id")
    platform = request.get("platform")
    time_str = request.get("scheduled_time")

    if not all([content_id, platform, time_str]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        scheduled_time = datetime.fromisoformat(time_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use ISO 8601.")

    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    new_schedule = Schedule(
        content_id=content_id, platform=platform,
        scheduled_time=scheduled_time, status="pending"
    )
    db.add(new_schedule)
    db.commit()

    logger.info(f"One-time schedule intent for content {content_id} created at {scheduled_time}")
    return {"message": "Content schedule intent created. The scheduler will pick it up shortly."}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 2009))
    host = os.getenv("HOST", "0.0.0.0")
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run("main:app", host=host, port=port, reload=reload)
