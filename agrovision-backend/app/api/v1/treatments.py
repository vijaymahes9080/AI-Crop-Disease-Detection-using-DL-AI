# app/api/v1/treatments.py
from fastapi import APIRouter, HTTPException, Depends
from app.services.recommendation import RecommendationEngine, RiskAssessment

router = APIRouter()
recommender = RecommendationEngine()

@router.get("/diseases/{disease_id}/treatment", response_model=RiskAssessment)
def get_disease_treatment(
    disease_id: int, 
    temperature: float, 
    humidity: float
):
    try:
        assessment = recommender.generate_treatment(
            disease_id=disease_id,
            temp=temperature,
            humidity=humidity
        )
        return assessment
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
