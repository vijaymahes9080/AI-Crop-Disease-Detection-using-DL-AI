# app/api/v1/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from typing import Optional

from app.api.dependencies.database import get_db
from app.models.database import DiagnosticScan, Crop

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(
    crop_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    # Set default date range if none specified (last 30 days)
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()

    # Base query filters
    query_filter = [
        DiagnosticScan.uploaded_at >= start_date,
        DiagnosticScan.uploaded_at <= end_date
    ]
    if crop_id:
        query_filter.append(DiagnosticScan.crop_id == crop_id)

    # 1. SCAN USAGE METRICS (Scans grouped by Date)
    usage_stats = db.query(
        cast(DiagnosticScan.uploaded_at, Date).label("scan_date"),
        func.count(DiagnosticScan.id).label("scan_count")
    ).filter(*query_filter)\
     .group_by(cast(DiagnosticScan.uploaded_at, Date))\
     .order_by("scan_date").all()

    # 2. DISEASE FREQUENCY DISTRIBUTION
    disease_freq = db.query(
        DiagnosticScan.detected_disease_name.label("disease_name"),
        func.count(DiagnosticScan.id).label("count")
    ).filter(*query_filter)\
     .group_by(DiagnosticScan.detected_disease_name)\
     .order_by(func.count(DiagnosticScan.id).desc()).all()

    # 3. ACCURACY INDEX (Average Confidence Score & Severity)
    accuracy_metrics = db.query(
        func.avg(DiagnosticScan.confidence_score).label("avg_confidence"),
        func.avg(DiagnosticScan.severity_pct).label("avg_severity")
    ).filter(*query_filter).first()

    return {
        "time_range": {"start": start_date, "end": end_date},
        "metrics": {
            "average_confidence": float(accuracy_metrics[0]) if accuracy_metrics[0] else 0.0,
            "average_severity_pct": float(accuracy_metrics[1]) if accuracy_metrics[1] else 0.0
        },
        "usage_over_time": [
            {"date": str(row.scan_date), "scans": row.scan_count} for row in usage_stats
        ],
        "disease_distribution": [
            {"disease": row.disease_name, "count": row.count} for row in disease_freq
        ]
    }

@router.get("/export")
def export_analytics(crop_id: Optional[int] = None, db: Session = Depends(get_db)):
    from app.services.export import generate_csv_report
    from fastapi.responses import StreamingResponse
    
    csv_io = generate_csv_report(db, crop_id)
    return StreamingResponse(
        csv_io,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scans_report.csv"}
    )

