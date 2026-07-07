# Model Explainability & Visual Interpretability Spec
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Visual Explainability Pipeline (`src/explain.py`)

This script implements **Grad-CAM (Gradient-weighted Class Activation Mapping)** in PyTorch to compute activation gradients on the final convolutional layer of a model, mapping them back to the input canvas. It also integrates **SHAP (SHapley Additive exPlanations)**.

```python
# training/explain.py
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import shap

# 1. GRAD-CAM IMPLEMENTATION
class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.features = None
        self.hook_layers()

    def hook_layers(self):
        def forward_hook(module, input, output):
            self.features = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        # Register forward and backward hooks on target convolutional layer
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_heatmap(self, input_tensor, class_idx=None):
        self.model.eval()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = torch.argmax(output, dim=1).item()

        self.model.zero_grad()
        class_loss = output[0, class_idx]
        class_loss.backward()

        # Global average pooling of gradients
        gradients = self.gradients.cpu().data.numpy()[0]
        features = self.features.cpu().data.numpy()[0]
        weights = np.mean(gradients, axis=(1, 2))

        # Weight the feature maps
        cam = np.zeros(features.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * features[i, :, :]

        # Apply ReLU activation and normalize
        cam = np.maximum(cam, 0)
        cam = cv2.resize(cam, (input_tensor.shape[2], input_tensor.shape[3]))
        cam = cam - np.min(cam)
        cam = cam / np.max(cam) if np.max(cam) != 0 else cam
        return cam

def overlay_heatmap(image_path, cam_heatmap, alpha=0.4):
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Generate colormap overlay
    heatmap = cv2.applyColorMap(np.uint8(255 * cam_heatmap), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    # Resize heatmap to match image size
    heatmap = cv2.resize(heatmap, (img_rgb.shape[1], img_rgb.shape[0]))
    
    # Blend image with heatmap overlay
    blended = cv2.addWeighted(img_rgb, 1 - alpha, heatmap, alpha, 0)
    return blended

# 2. SHAP MODEL EXPLAINER
def generate_shap_values(model, background_images, test_image):
    model.eval()
    # background_images should be a representative batch tensor (~50-100 images)
    explainer = shap.GradientExplainer(model, background_images)
    shap_values = explainer.shap_values(test_image)
    return shap_values
```

---

## 2. FastAPI Backend API Controller Integration

This endpoint receives an image, runs inference, generates a Grad-CAM heatmap, uploads it to S3, and returns the classification metadata.

```python
# app/api/v1/scans.py
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import cv2
import numpy as np

from app.api.dependencies.database import get_db
from app.services.s3 import upload_to_s3
from training.explain import GradCAM, overlay_heatmap
from training.models import get_model

router = APIRouter()

# Instantiate target models globally to cache weights in GPU memory
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
num_classes = 4 # E.g., Tomato/Coffee disease classes
model = get_model("efficientnet", num_classes, pretrained=False)
model.load_state_dict(torch.load("checkpoints/best-model/pytorch_model.bin", map_location=device))
model.to(device)

# Target the final convolutional layer for Grad-CAM
target_layer = model.features[-1]
cam_extractor = GradCAM(model, target_layer)

@router.post("/analyze")
async def analyze_scan(
    crop_category_id: int, 
    latitude: float, 
    longitude: float, 
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Read raw image
    image_bytes = await image.read()
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
```

---

## 3. React Frontend UI Integration (`HeatmapViewer.jsx`)

Renders a custom image card that allows the user to slide or toggle between the clean capture and the model's activation heatmap.

```javascript
// src/features/diagnostics/components/HeatmapViewer.jsx
import React, { useState } from 'react';

export default function HeatmapViewer({ originalImage, heatmapImage, diseaseName, confidence }) {
  const [opacity, setOpacity] = useState(0.5); // Default blend factor
  const [showOverlay, setShowOverlay] = useState(true);

  return (
    <div className="glass-surface p-6 rounded-2xl max-w-md mx-auto shadow-2xl">
      <h3 className="text-lg font-semibold text-slate-50 mb-2">Model Focus Area</h3>
      <p className="text-sm text-slate-400 mb-4">
        Below is the activation map highlighting the leaf spots that informed the classification.
      </p>

      {/* Layer Stack Frame */}
      <div className="relative aspect-square w-full rounded-xl overflow-hidden bg-slate-900 border border-slate-700">
        {/* Underlay: Original Leaf Photo */}
        <img 
          src={originalImage} 
          alt="Original leaf capture" 
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* Overlay: Heatmap */}
        {showOverlay && (
          <img 
            src={heatmapImage} 
            alt="Grad-CAM activation heatmap overlay" 
            className="absolute inset-0 w-full h-full object-cover transition-opacity duration-150"
            style={{ opacity: opacity }}
          />
        )}
      </div>

      {/* Opacity Control Slider */}
      <div className="mt-6 space-y-4">
        <div className="flex items-center justify-between">
          <label htmlFor="opacity-slider" className="text-sm font-medium text-slate-200">
            Heatmap Intensity
          </label>
          <button 
            onClick={() => setShowOverlay(!showOverlay)}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-colors ${
              showOverlay ? 'bg-emerald-500 text-slate-950' : 'bg-slate-700 text-slate-300'
            }`}
          >
            {showOverlay ? 'Hide Overlay' : 'Show Overlay'}
          </button>
        </div>

        <input 
          id="opacity-slider"
          type="range" 
          min="0" 
          max="1" 
          step="0.05"
          value={opacity}
          disabled={!showOverlay}
          onChange={(e) => setOpacity(parseFloat(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500 disabled:opacity-50"
        />

        {/* Diagnostic Metadata Footer */}
        <div className="border-t border-slate-700 pt-4 flex justify-between items-center">
          <div>
            <span className="text-xs text-slate-400 block uppercase tracking-wider">Prediction</span>
            <span className="text-base font-bold text-slate-100">{diseaseName}</span>
          </div>
          <div className="text-right">
            <span className="text-xs text-slate-400 block uppercase tracking-wider">Confidence</span>
            <span className="text-base font-bold text-emerald-400">{(confidence * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

*This model explainability implementation ensures diagnostics transparency and clinical verification support on the AgroVision AI platform.*
