# training/models.py
import torch
import torch.nn as nn
import torchvision.models as models

# 1. BASELINE CUSTOM CNN
class CustomCNN(nn.Module):
    def __init__(self, num_classes):
        super(CustomCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # 112x112
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # 56x56
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  # 28x28
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 28 * 28, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))

# 2. MODEL FACTORY LOADER
def get_model(model_name: str, num_classes: int, pretrained: bool = True):
    model_name = model_name.lower()
    
    if model_name == "cnn":
        return CustomCNN(num_classes)
        
    elif model_name == "mobilenetv3":
        # Load weights explicitly to avoid deprecation warnings
        w = models.MobileNet_V3_Large_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v3_large(weights=w)
        # Substitute classifier head
        in_features = model.classifier[3].in_features
        model.classifier[3] = nn.Linear(in_features, num_classes)
        return model
        
    elif model_name == "efficientnet":
        w = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=w)
        # Substitute classifier head
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        return model
        
    elif model_name == "resnet50":
        w = models.ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=w)
        # Substitute classifier head
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
        return model
        
    else:
        raise ValueError(f"Unknown model architecture: {model_name}")
