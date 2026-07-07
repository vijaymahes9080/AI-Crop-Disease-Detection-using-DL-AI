# AgroVision AI — Machine Learning Pipeline

This module implements PyTorch models, data pipeline triggers, explainability engines (Grad-CAM/SHAP), and edge compilation tools.

## Structure
- `/training/`: Contains dataset loading, models (Custom CNN, MobileNetV3, EfficientNet, ResNet50), training loops, and evaluations.
- `/inference/`: Serving handlers for TorchServe.
- `/scripts/`: Compilation scripts to ONNX and quantized TFLite graphs.

## Training Commands
To execute model training:
```bash
python training/train.py
```
To run evaluation:
```bash
python training/evaluate.py
```
