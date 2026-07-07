# app/services/inference_client.py
import httpx
from fastapi import HTTPException

TORCHSERVE_URL = "http://localhost:8080/predictions/crop_disease"

async def get_model_inference(image_bytes: bytes) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Post binary image payload directly to TorchServe endpoints
            response = await client.post(
                TORCHSERVE_URL,
                content=image_bytes,
                headers={"Content-Type": "application/octet-stream"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Inference engine failure code {response.status_code}: {response.text}"
                )
                
            prediction = response.json()
            return {
                "class_id": prediction.get("class_id"),
                "confidence": prediction.get("confidence"),
                "severity_pct": prediction.get("severity_pct", 0.0),
                "heatmap_s3_key": prediction.get("heatmap_s3_key")
            }
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Connection failed to TorchServe cluster: {exc}"
            )
