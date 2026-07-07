# Agronomic Recommendation & Treatment System Spec
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Structured Agronomic Knowledge Base (`data/treatments.json`)

The platform's knowledge base acts as a curated repository of verified agricultural remedies.

```json
{
  "diseases": [
    {
      "id": 1,
      "name": "Potato Late Blight (Phytophthora infestans)",
      "cause": "Water-mold pathogen spreading rapidly under cool, wet conditions (high humidity, temperature 15-20°C).",
      "prevention": [
        "Use certified disease-free seed tubers.",
        "Ensure wide crop spacing to promote leaf drying.",
        "Avoid overhead irrigation; use drip irrigation systems."
      ],
      "risk_level": "CRITICAL",
      "treatments": {
        "organic": {
          "title": "Copper compounds & bio-fungicides",
          "steps": [
            "Apply liquid copper fungicide sprays thoroughly on leaves.",
            "Use Bacillus subtilis strain QST 713 bio-controls on early foliage."
          ],
          "dosage": "Dilute 2.5 oz copper solution per gallon of water. Spray every 7-10 days."
        },
        "chemical": {
          "title": "Fungicide mixtures (Mancozeb or Chlorothalonil)",
          "steps": [
            "Apply Chlorothalonil 720 SFT sprays at early vine growth.",
            "Rotate with metalaxyl-containing mixtures to prevent resistance."
          ],
          "dosage": "1.5 lb Chlorothalonil per acre. Observe pre-harvest interval of 5 days."
        }
      }
    },
    {
      "id": 2,
      "name": "Coffee Leaf Rust (Hemileia vastatrix)",
      "cause": "Fungal spores landing on leaves, requiring free water on the leaf surface for over 24 hours to germinate.",
      "prevention": [
        "Prune shade trees to increase direct sunlight exposure.",
        "Remove and burn fallen infected coffee leaves.",
        "Plant rust-resistant cultivars (e.g., Castillo, Catimor)."
      ],
      "risk_level": "WARNING",
      "treatments": {
        "organic": {
          "title": "Mineral oils & copper sulfate mixtures",
          "steps": [
            "Spray copper hydroxide mixtures on the underside of leaves.",
            "Apply neem oil extracts dynamically to restrict spore germination."
          ],
          "dosage": "1% Copper Hydroxide mix. Apply at onset of rainy season."
        },
        "chemical": {
          "title": "Triazole systemic fungicides",
          "steps": [
            "Apply Cyproconazole or Triadimefon directly to foliar structures.",
            "Spray only when rust severity indexes cross 5%."
          ],
          "dosage": "0.5 Liters Cyproconazole per hectare. Max 2 applications per year."
        }
      }
    }
  ]
}
```

---

## 2. Weather-Aware Risk Decision Engine (`services/recommendation.py`)

This service dynamically adjusts a pathogen's risk index by merging the AI model's diagnosis with real-time field weather readings (humidity, temperature).

```python
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
    def __init__(self, kb_path: str = "data/treatments.json"):
        with open(kb_path, "r") as f:
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
```

---

## 3. FastAPI Recommendation API Endpoint

Returns weather-adjusted remedies dynamically to requests.

```python
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
```

---

## 4. React Display Component (`TreatmentGuide.jsx`)

Renders a tab-controlled treatment view mapping organic vs. chemical inputs.

```javascript
// src/features/diagnostics/components/TreatmentGuide.jsx
import React, { useState } from 'react';

export default function TreatmentGuide({ remedyData, riskLevel }) {
  const [activeTab, setActiveTab] = useState('organic'); // Tabs: 'organic' or 'chemical'
  const remedies = remedyData.treatments[activeTab];

  return (
    <div className="glass-surface p-6 rounded-2xl max-w-lg mx-auto border border-slate-700 space-y-6">
      {/* Header Info */}
      <div className="flex justify-between items-start">
        <div>
          <h4 className="text-xs text-slate-400 uppercase tracking-wider">Agronomic Remedy Guide</h4>
          <h3 className="text-lg font-bold text-slate-100">Pathogen Treatment Protocols</h3>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wide ${
          riskLevel === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
          riskLevel === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
          'bg-green-500/10 text-green-400 border border-green-500/20'
        }`}>
          {riskLevel} Risk
        </span>
      </div>

      <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-800 text-sm">
        <strong className="text-slate-200 block mb-1">Biological Cause:</strong>
        <p className="text-slate-400 leading-relaxed">{remedyData.cause}</p>
      </div>

      {/* Selector Tabs Toggle */}
      <div className="grid grid-cols-2 gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => setActiveTab('organic')}
          className={`py-2 text-sm font-semibold rounded-lg transition-all ${
            activeTab === 'organic' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Organic Options
        </button>
        <button
          onClick={() => setActiveTab('chemical')}
          className={`py-2 text-sm font-semibold rounded-lg transition-all ${
            activeTab === 'chemical' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Chemical Inputs
        </button>
      </div>

      {/* Remedies Action List */}
      <div className="space-y-4">
        <div>
          <span className="text-xs text-slate-400 uppercase font-semibold">Recommended Steps</span>
          <ul className="list-disc pl-5 mt-2 space-y-2 text-sm text-slate-300">
            {remedies.steps.map((step, idx) => (
              <li key={idx} className="leading-relaxed">{step}</li>
            ))}
          </ul>
        </div>

        <div className="border-t border-slate-700/60 pt-4">
          <span className="text-xs text-slate-400 uppercase font-semibold block">Dosage Details</span>
          <p className="text-sm font-medium text-emerald-400 mt-1">{remedies.dosage}</p>
        </div>
      </div>

      {/* Prevention Section */}
      <div className="border-t border-slate-700/60 pt-4 space-y-2">
        <span className="text-xs text-slate-400 uppercase font-semibold block">Preventative Farm Guidelines</span>
        <ul className="list-decimal pl-5 space-y-1.5 text-xs text-slate-400 leading-relaxed">
          {remedyData.prevention.map((prev, idx) => (
            <li key={idx}>{prev}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
```

---

*This recommendation workflow manages database search matrices, weather-adjusted risk assessments, and accessible user instructions on the AgroVision AI platform.*
