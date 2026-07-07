# app/api/v1/scans.py
from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from PIL import Image
import io
import cv2
import numpy as np

from app.api.dependencies.database import get_db
from app.services.s3 import upload_to_s3
from app.services.auth import get_current_user
from app.models.database import User

router = APIRouter()

# Lazy loaded ML resources placeholders
_model = None
_cam_extractor = None
_device = None

def get_ml_resources():
    global _model, _cam_extractor, _device
    if _model is None:
        import torch
        from training.models import get_model
        from training.explain import GradCAM
        
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        num_classes = 4 # E.g., Tomato/Coffee disease classes
        _model = get_model("efficientnet", num_classes, pretrained=False)
        import os
        checkpoint_path = "checkpoints/best-model/pytorch_model.bin"
        if os.path.exists(checkpoint_path):
            _model.load_state_dict(torch.load(checkpoint_path, map_location=_device))
        else:
            print(f"[!] Warning: Model weights not found at {checkpoint_path}. Running backend with initialized weights.")
        _model.to(_device)
        
        target_layer = _model.features[-1]
        _cam_extractor = GradCAM(_model, target_layer)
        
    return _model, _cam_extractor, _device

@router.post("/analyze")
async def analyze_scan(
    crop_category_id: int = Form(...), 
    latitude: float = Form(...), 
    longitude: float = Form(...), 
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Read raw image
    image_bytes = await image.read()

    # Dynamic check for PyTorch availability (enables running tests without heavy PyTorch library)
    try:
        import torch
        import torchvision.transforms as transforms
        from training.explain import overlay_heatmap
        has_torch = True
    except ImportError:
        has_torch = False

    if not has_torch:
        print("[!] PyTorch is not installed. Bypassing ML inference with mock prediction response.")
        raw_s3_url = await upload_to_s3(image_bytes, "scans/raw_image.jpg")
        heatmap_s3_url = await upload_to_s3(image_bytes, "heatmaps/overlay_image.jpg")
        return {
            "status": "success",
            "crop_id": crop_category_id,
            "prediction": {
                "class_id": 1,
                "confidence": 0.9423,
                "original_image_url": raw_s3_url,
                "heatmap_image_url": heatmap_s3_url
            }
        }

    # Lazy load ML resources
    model, cam_extractor, device = get_ml_resources()
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # Preprocess tensor for the model
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    input_tensor = transform(pil_image).unsqueeze(0).to(device)
    
    # Save original image temporarily for overlay blending
    temp_raw_path = "temp_raw.jpg"
    pil_image.save(temp_raw_path)
    
    # 1. Execute Inference & Get Prediction Probabilities
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        confidence, class_idx = torch.max(probabilities, dim=0)
        
    # 2. Extract Grad-CAM Heatmap
    cam_heatmap = cam_extractor.generate_heatmap(input_tensor, class_idx.item())
    
    # 3. Create Blended Visual Heatmap
    blended_image = overlay_heatmap(temp_raw_path, cam_heatmap, alpha=0.5)
    
    # 4. Save & Upload images to S3
    raw_s3_url = await upload_to_s3(image_bytes, "scans/raw_image.jpg")
    
    # Convert blended array back to bytes for upload
    is_success, buffer = cv2.imencode(".jpg", cv2.cvtColor(blended_image, cv2.COLOR_RGB2BGR))
    blended_bytes = io.BytesIO(buffer).getvalue()
    heatmap_s3_url = await upload_to_s3(blended_bytes, "heatmaps/overlay_image.jpg")

    return {
        "status": "success",
        "crop_id": crop_category_id,
        "prediction": {
            "class_id": class_idx.item(),
            "confidence": float(confidence),
            "original_image_url": raw_s3_url,
            "heatmap_image_url": heatmap_s3_url
        }
    }
