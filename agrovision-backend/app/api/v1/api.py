# app/api/v1/api.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.api.dependencies.database import get_db
from app.services.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models.database import User, DiagnosticScan
from app.schemas.scan import UserRegister, Token, ScanResponse, RegionalOutbreakMetric

router = APIRouter()

# Include feature sub-routers
from app.api.v1.scans import router as scans_router
from app.api.v1.treatments import router as treatments_router
from app.api.v1.analytics import router as analytics_router

router.include_router(scans_router, prefix="/scans", tags=["scans"])
router.include_router(treatments_router, tags=["treatments"])
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# 1. USER REGISTER
@router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.phone_number == user_in.phone_number).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    new_user = User(
        phone_number=user_in.phone_number,
        name=user_in.name,
        password_hash=hash_password(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(data={"sub": new_user.phone_number})
    return {"access_token": token, "token_type": "bearer"}

# 2. USER LOGIN
@router.post("/auth/login", response_model=Token)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Form username matches phone_number key
    user = db.query(User).filter(User.phone_number == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect phone number or password")
    
    token = create_access_token(data={"sub": user.phone_number})
    return {"access_token": token, "token_type": "bearer"}

# 3. GET SCANS HISTORY
@router.get("/scans/history", response_model=List[ScanResponse])
def get_history(
    skip: int = 0, 
    limit: int = 20, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    scans = db.query(DiagnosticScan)\
              .filter(DiagnosticScan.user_id == current_user.id)\
              .order_by(DiagnosticScan.uploaded_at.desc())\
              .offset(skip).limit(limit).all()
              
    # Adapt database model arrays into Pydantic shape responses
    response = []
    for scan in scans:
        response.append(ScanResponse(
            id=scan.id,
            crop_id=scan.crop_id,
            user_id=scan.user_id,
            original_image_url=scan.image_url,
            uploaded_at=scan.uploaded_at,
            prediction={
                "class_id": 1,
                "disease_name": scan.detected_disease_name,
                "confidence": float(scan.confidence_score),
                "severity_pct": float(scan.severity_pct) if scan.severity_pct else 0.0,
                "heatmap_url": scan.heatmap_url
            }
        ))
    return response

# 4. GET SPATIAL OUTBREAKS
@router.get("/scans/analytics", response_model=List[RegionalOutbreakMetric])
def get_analytics(
    latitude: float, 
    longitude: float, 
    radius_km: float = 50.0, 
    db: Session = Depends(get_db)
):
    # In production, uses PostGIS spatial geometry indexing:
    # ST_DWithin(coordinates, ST_MakePoint(lon, lat), radius)
    # Mocking location fetch:
    scans = db.query(DiagnosticScan).limit(10).all()
    return [
        RegionalOutbreakMetric(
            disease_id=1,
            disease_name=scan.detected_disease_name,
            scan_count=12,
            latitude=scan.latitude,
            longitude=scan.longitude
        ) for scan in scans
    ]
