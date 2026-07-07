# app/models/database.py
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import TypeDecorator, CHAR
import uuid
import datetime

Base = declarative_base()

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise CHAR(36), storing as stringified hex.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID as PG_UUID
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            return uuid.UUID(value)

class User(Base):
    __tablename__ = "users"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
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
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), index=True)
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
