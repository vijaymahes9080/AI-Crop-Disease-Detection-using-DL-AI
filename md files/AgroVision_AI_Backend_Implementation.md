# Backend Implementation Specification (FastAPI)
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Pydantic Serialization Schemas (`schemas/`)

These schemas serialize request inputs and format output payloads, automatically generating the Swagger/OpenAPI documentation schema.

```python
# app/schemas/scan.py
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class UserRegister(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PredictionResult(BaseModel):
    class_id: int
    disease_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity_pct: float
    heatmap_url: Optional[str]

class ScanCreateInput(BaseModel):
    crop_id: int
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

class ScanResponse(BaseModel):
    id: UUID
    crop_id: int
    user_id: UUID
    prediction: PredictionResult
    original_image_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class RegionalOutbreakMetric(BaseModel):
    disease_id: int
    disease_name: str
    scan_count: int
    latitude: float
    longitude: float
```

---

## 2. SQLAlchemy Declarative Models (`models/`)

Maps database tables to Python objects using standard relationships.

```python
# app/models/database.py
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), default="farmer", nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    
    scans = relationship("DiagnosticScan", back_populates="user")

class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    common_name = Column(String(100), unique=True, nullable=False)
    scientific_name = Column(String(150), nullable=False)
    family = Column(String(100), nullable=False)

class DiagnosticScan(Base):
    __tablename__ = "diagnostic_scans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    detected_disease_name = Column(String(150), nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    severity_pct = Column(Numeric(5, 2))
    image_url = Column(String(255), nullable=False)
    heatmap_url = Column(String(255))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="scans")
```

---

## 3. JWT Security & Auth Services (`services/auth.py`)

Handles password encryption hashing (using `bcrypt`) and JWT extraction.

```python
# app/services/auth.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.database import User
from app.api.dependencies.database import get_db

SECRET_KEY = "super_secret_jwt_signature_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 Hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if user is None:
        raise credentials_exception
    return user
```

---

## 4. API Endpoint Routers (`api/v1/`)

Provides structured endpoints for registration, login, uploads, and data query requests.

```python
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
```

---

## 5. Middleware & Error Handlers

Configures CORS boundaries and creates standard JSON error responses.

```python
# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.api import router as v1_router

app = FastAPI(
    title="AgroVision AI API",
    description="Backend services for crop disease detection scans",
    version="1.0.0"
)

# CORS Boundaries configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error Handling Middleware
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error_code": exc.status_code, "message": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "error_code": 500, "message": "An unexpected error occurred on the server"},
    )

app.include_router(v1_router, prefix="/api/v1")
```

---

## 6. Backend Integration Tests (`tests/`)

Executes integration checks against local test databases.

```python
# tests/test_backend.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_base
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.dependencies.database import get_db
from app.models.database import Base

# Setup clean in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_user_flow():
    # 1. Test registration
    reg_response = client.post("/api/v1/auth/register", json={
        "phone_number": "+919999999999",
        "name": "Test Farmer",
        "password": "securepassword123"
    })
    assert reg_response.status_code == 201
    assert "access_token" in reg_response.json()
    
    # 2. Test login
    login_response = client.post("/api/v1/auth/login", data={
        "username": "+919999999999",
        "password": "securepassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Test history endpoint authentication guard
    history_response = client.get(
        "/api/v1/scans/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert history_response.status_code == 200
    assert isinstance(history_response.json(), list)
```

---

*This backend architecture spec provides the routing, validation layers, exception guards, database model links, and test setups for the AgroVision platform.*
