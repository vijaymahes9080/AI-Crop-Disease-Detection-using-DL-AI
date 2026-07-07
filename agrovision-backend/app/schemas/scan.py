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
