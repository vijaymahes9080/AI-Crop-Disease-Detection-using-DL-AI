# app/services/recommendation.py
import json
from pydantic import BaseModel
from typing import Dict, Any

class RiskAssessment(BaseModel):
    disease_id: int
    disease_name: str
    base_risk: str
    adjusted_risk: str
    remedy_payload: Dict[str, Any]

def calculate_adjusted_risk(base_risk: str, temp: float, humidity: float) -> str:
    # High humidity (>75%) and warm temperatures (15-28°C) catalyze fungal outbreaks
    if humidity > 75.0 and (15.0 <= temp <= 28.0):
        if base_risk == "WARNING":
            return "CRITICAL"
        return base_risk
    # Low humidity reduces spore propagation rate
    elif humidity < 40.0:
        if base_risk == "CRITICAL":
            return "WARNING"
        elif base_risk == "WARNING":
            return "INFO"
    return base_risk

class RecommendationEngine:
    def __init__(self, kb_path: str = None):
        if kb_path is None:
            import os
            kb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "treatments.json"))
        with open(kb_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)

    def generate_treatment(self, disease_id: int, temp: float, humidity: float) -> RiskAssessment:
        # Find target disease in agronomic JSON knowledge base
        disease_data = next((d for d in self.kb["diseases"] if d["id"] == disease_id), None)
        if not disease_data:
            raise ValueError(f"Disease ID {disease_id} not found in KB")

        base_risk = disease_data["risk_level"]
        adjusted_risk = calculate_adjusted_risk(base_risk, temp, humidity)

        return RiskAssessment(
            disease_id=disease_id,
            disease_name=disease_data["name"],
            base_risk=base_risk,
            adjusted_risk=adjusted_risk,
            remedy_payload={
                "cause": disease_data["cause"],
                "prevention": disease_data["prevention"],
                "treatments": disease_data["treatments"]
            }
        )
