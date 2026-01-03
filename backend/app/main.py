from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import shutil
import os
import uuid
import logging
import secrets

from fastapi.staticfiles import StaticFiles
from .verifier import MotionVerifierWrapper
from .c2pa_signer import C2PASignerService
from . import models, database, auth

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize DB Tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="VeriPhysics Cloud")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configuration
CLI_PATH = os.environ.get("VERIPHYSICS_CLI_PATH", "/usr/local/bin/vp_cli")
UPLOAD_DIR = "/tmp/veriphysics_uploads"
SIGNED_DIR = "/tmp/veriphysics_signed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SIGNED_DIR, exist_ok=True)

app.mount("/files", StaticFiles(directory=SIGNED_DIR), name="files")

try:
    verifier = MotionVerifierWrapper(CLI_PATH)
except FileNotFoundError as e:
    logger.warning(f"Verifier CLI not found: {e}")
    verifier = None

# C2PA Setup
CERT_PATH = "backend/certs/ps256.crt"
KEY_PATH = "backend/certs/ps256.pem"
signer_service = None
if os.path.exists(CERT_PATH) and os.path.exists(KEY_PATH):
    try:
        signer_service = C2PASignerService(CERT_PATH, KEY_PATH)
        logger.info("C2PA Signer initialized")
    except Exception as e:
        logger.error(f"Failed to init C2PA Signer: {e}")
else:
    logger.warning("C2PA Certs not found, signing disabled")

def get_db():
    yield from database.get_db()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except auth.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# Actually, let's redefine get_api_key_user cleanly
from fastapi import Header
async def get_current_user_from_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    key_record = db.query(models.ApiKey).filter(models.ApiKey.key == x_api_key, models.ApiKey.is_active == True).first()
    if not key_record:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return key_record.user_id

def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# --- AUTH ENDPOINTS ---

@app.post("/register")
def register(user: dict, db: Session = Depends(get_db)):
    # Expects {"email": "...", "password": "..."}
    # Simplified validation
    email = user.get("email")
    password = user.get("password")
    if not email or not password:
        raise HTTPException(400, "Email and password required")
        
    fake_user = db.query(models.User).filter(models.User.email == email).first()
    if fake_user:
        raise HTTPException(400, "Email already registered")
    
    hashed_pwd = auth.get_password_hash(password)
    # Check if this is the first user, if so, make them admin
    is_admin = db.query(models.User).count() == 0
    new_user = models.User(email=email, hashed_password=hashed_pwd, is_admin=is_admin)
    db.add(new_user)
    db.commit()
    return {"status": "User created", "is_admin": is_admin}

@app.get("/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "id": current_user.id
    }

@app.get("/admin/stats")
def get_admin_stats(current_user: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_jobs = db.query(models.VerificationJob).count()
    verified_jobs = db.query(models.VerificationJob).filter(models.VerificationJob.is_consistent == True).count()
    failed_jobs = db.query(models.VerificationJob).filter(models.VerificationJob.is_consistent == False).count()
    processing_jobs = db.query(models.VerificationJob).filter(models.VerificationJob.status == "PROCESSING").count()
    users_count = db.query(models.User).count()
    
    return {
        "total_jobs": total_jobs,
        "verified_jobs": verified_jobs,
        "failed_jobs": failed_jobs,
        "processing_jobs": processing_jobs,
        "users_count": users_count
    }

@app.get("/admin/jobs")
def get_all_jobs(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    jobs = db.query(models.VerificationJob).order_by(models.VerificationJob.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": j.id,
            "status": j.status,
            "score": j.score,
            "verified": j.is_consistent,
            "created_at": j.created_at,
            "filename": j.video_filename,
            "user_id": j.user_id,
            "message": j.message
        }
        for j in jobs
    ]

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api-keys")
def create_api_key(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_key_str = "vp_" + secrets.token_urlsafe(32)
    new_key = models.ApiKey(key=new_key_str, user_id=current_user.id)
    db.add(new_key)
    db.commit()
    return {"api_key": new_key_str}

@app.get("/api-keys")
def list_api_keys(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(models.ApiKey).filter(models.ApiKey.user_id == current_user.id).all()
    return [{"key": k.key, "active": k.is_active, "created": k.created_at} for k in keys]

def process_verification(job_id: int, video_path: str, gyro_path: str, db: Session):
    try:
        logger.info(f"Starting verification for Job {job_id}")
        
        # update status to PROCESSING
        job = db.query(models.VerificationJob).filter(models.VerificationJob.id == job_id).first()
        if job:
            job.status = "PROCESSING"
            db.commit()

        if not verifier:
             raise Exception("Verifier engine unavailable")

        result = verifier.verify(video_path, gyro_path)
        
        signed_url = None
        if result.get("verified") and signer_service:
            try:
                output_filename = f"signed_{os.path.basename(video_path)}"
                output_path = os.path.join(SIGNED_DIR, output_filename)
                
                # Prepare assertion data
                verification_data = {
                    "score": result.get("score"),
                    "details": result.get("details"),
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "verifier": "VeriPhysics Cloud v1"
                }
                
                signer_service.sign_video(video_path, output_path, verification_data)
                signed_url = f"/files/{output_filename}"
                logger.info(f"Video signed: {signed_url}")
            except Exception as e:
                logger.error(f"Signing failed: {e}")

        # Update Job
        # Re-fetch to avoid detach issues if needed, but session is scoped
        job = db.query(models.VerificationJob).filter(models.VerificationJob.id == job_id).first()
        if job:
            job.status = "COMPLETED"
            job.score = result.get("score")
            job.is_consistent = result.get("verified")
            job.message = result.get("message")
            job.signed_url = signed_url
            db.commit()
            
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job = db.query(models.VerificationJob).filter(models.VerificationJob.id == job_id).first()
        if job:
            job.status = "ERROR"
            job.message = str(e)
            db.commit()
            
    finally:
        # Cleanup files
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(gyro_path):
            os.remove(gyro_path)

@app.post("/verify", response_model=models.VerificationResponse)
async def verify_bundle(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
    gyro: UploadFile = File(...),
    x_signature: str = Header(None),
    user_id: int = Depends(get_current_user_from_key),
    db: Session = Depends(get_db)
):
    """
    Submit a video + gyro bundle for verification.
    Requires API Key.
    """
    # 1. verify signature (Mock for MVP: just check presence if we enforced it)
    if x_signature:
        logger.info(f"Received Signature: {x_signature[:10]}...")
        # In PROD: Fetch User's Public Key from DB (uploaded previously via SDK) and verify.
        # For now, we just log it to prove "Active Provenance" capability.
    
    # 2. Save Files
    task_uuid = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_DIR, f"{task_uuid}_{video.filename}")
    gyro_path = os.path.join(UPLOAD_DIR, f"{task_uuid}_{gyro.filename}")
    
    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)
    with open(gyro_path, "wb") as buffer:
        shutil.copyfileobj(gyro.file, buffer)
        
    # 2. Create Job Record
    job = models.VerificationJob(
        video_filename=video.filename,
        gyro_filename=gyro.filename,
        status="PENDING",
        user_id=user_id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # 3. Offload task
    background_tasks.add_task(process_verification, job.id, video_path, gyro_path, database.SessionLocal())
    
    return {
        "id": job.id,
        "status": "PENDING",
        "message": "Job submitted successfully"
    }

@app.get("/jobs")
def list_jobs(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find all API keys for this user? No, jobs are linked to user_id directly now (via verify endpoint).
    # Wait, verify endpoint uses `user_id` from `get_current_user_from_key`.
    # `get_current_user_from_key` returns `user_id` (int).
    # So we are good.
    jobs = db.query(models.VerificationJob).filter(models.VerificationJob.user_id == current_user.id).all()
    # Return simple list
    return [
        {
            "id": j.id,
            "status": j.status,
            "score": j.score,
            "verified": j.is_consistent,
            "created_at": j.created_at,
            "filename": j.video_filename,
            "signed_url": j.signed_url
        }
        for j in jobs
    ]

@app.get("/jobs/{job_id}", response_model=models.VerificationResponse)
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.VerificationJob).filter(models.VerificationJob.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
        
    return {
        "id": job.id,
        "status": job.status,
        "score": job.score,
        "verified": job.is_consistent,
        "message": job.message,
        "signed_url": job.signed_url
    }
