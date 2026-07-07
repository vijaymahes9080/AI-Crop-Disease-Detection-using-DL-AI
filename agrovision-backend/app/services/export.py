# app/services/export.py
import csv
import io
from sqlalchemy.orm import Session
from app.models.database import DiagnosticScan

def generate_csv_report(db: Session, crop_id: int = None) -> io.BytesIO:
    query = db.query(DiagnosticScan)
    if crop_id:
        query = query.filter(DiagnosticScan.crop_id == crop_id)
    
    scans = query.order_by(DiagnosticScan.uploaded_at.desc()).all()
    
    # Write to memory buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header row
    writer.writerow([
        "Scan ID", "Crop ID", "Detected Pathogen", 
        "Confidence Score", "Severity Pct", 
        "Latitude", "Longitude", "Timestamp"
    ])
    
    # Write row details
    for scan in scans:
        writer.writerow([
            str(scan.id),
            scan.crop_id,
            scan.detected_disease_name,
            float(scan.confidence_score),
            float(scan.severity_pct) if scan.severity_pct else 0.0,
            scan.latitude,
            scan.longitude,
            scan.uploaded_at.isoformat()
        ])
        
    # Convert string stream to binary bytes
    bytes_io = io.BytesIO()
    bytes_io.write(output.getvalue().encode('utf-8'))
    bytes_io.seek(0)
    return bytes_io
