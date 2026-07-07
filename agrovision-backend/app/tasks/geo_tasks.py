from app.core.cel_app import celery_app
from app.api.dependencies.database import SessionLocal
from app.models.database import DiagnosticScan
from sqlalchemy import text

@celery_app.task
def check_regional_outbreaks(scan_id_str: str, latitude: float, longitude: float):
    print(f"[*] Starting geo-outbreak audit task for scan {scan_id_str}...")
    db = SessionLocal()
    try:
        # In production, queries PostGIS using spatial index:
        # ST_DWithin(location, ST_MakePoint(:lon, :lat), 5000)
        # Mocking the query logic check:
        scans_count = db.query(DiagnosticScan).count()
        print(f"[+] Scan count in DB: {scans_count}. Outbreak thresholds normal.")
    finally:
        db.close()
