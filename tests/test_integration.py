# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.dependencies.database import get_db
from app.models.database import Base, Crop, DiagnosticScan

# SQLite in-memory setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Populate mock crops
    db = TestingSessionLocal()
    if not db.query(Crop).filter(Crop.common_name == "Tomato").first():
        db.add(Crop(common_name="Tomato", scientific_name="Solanum lycopersicum", family="Solanaceae"))
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_scan_db_logging():
    # Simulate API post scan
    # Mocking authenticated post user check (simplified bypass)
    db = TestingSessionLocal()
    new_scan = DiagnosticScan(
        crop_id=1,
        detected_disease_name="Tomato Late Blight",
        confidence_score=0.9234,
        severity_pct=15.5,
        image_url="http://s3.aws.com/raw.jpg",
        latitude=12.97,
        longitude=77.59
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    
    assert new_scan.id is not None
    assert new_scan.detected_disease_name == "Tomato Late Blight"
    db.close()
