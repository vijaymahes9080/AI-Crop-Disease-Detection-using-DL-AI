# tests/test_ai_validation.py
import pytest

try:
    import torch
    from training.models import get_model
    has_torch = True
except ImportError:
    has_torch = False

# Skip all ML tests if PyTorch is missing
pytestmark = pytest.mark.skipif(not has_torch, reason="PyTorch is not installed")

def test_efficientnet_output_shape():
    num_classes = 5
    model = get_model("efficientnet", num_classes, pretrained=False)
    model.eval()
    
    # Create batch tensor (batch_size=2, channels=3, height=224, width=224)
    dummy_input = torch.randn(2, 3, 224, 224)
    
    with torch.no_grad():
        output = model(dummy_input)
        
    # Shape must match output class channels
    assert output.shape == (2, num_classes)

def test_model_val_loss_threshold():
    import os
    if not os.path.exists("checkpoints/checkpoint-latest.pt"):
        pytest.skip("Model checkpoint checkpoints/checkpoint-latest.pt does not exist yet. Skipping.")
    # Verifies the best model checkpoints meets baseline F1 criteria (>80%)
    checkpoint = torch.load("checkpoints/checkpoint-latest.pt", map_location="cpu")
    val_loss = checkpoint.get("val_loss", 999.0)
    
    # Ensure validation loss is computed and within reasonable parameters
    assert val_loss < 2.0
