# Deep Learning Model & Training Pipeline Spec
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Deep Learning Architectures (`models/`)

This implementation details the loader configurations for a baseline **Custom CNN**, **MobileNetV3**, **EfficientNet-B0**, and **ResNet-50** using PyTorch.

```python
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
```

---

## 2. Advanced Training Pipeline (`src/train.py`)

This pipeline features **GPU execution**, **dynamic checkpointing**, and **auto-saving of the best model weights** matching HuggingFace Transformer workflows.

```python
# training/train.py
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from models import get_model

# 1. Data Loaders
def get_data_loaders(data_dir, batch_size=32):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    train_dataset = datasets.ImageFolder(os.path.join(data_dir, "train"), transform=transform)
    val_dataset = datasets.ImageFolder(os.path.join(data_dir, "val"), transform=transform)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    return train_loader, val_loader, len(train_dataset.classes)

# 2. Main Training Loop
def train_model(model_name, data_dir, epochs=10, lr=1e-4, checkpoint_dir="checkpoints"):
    os.makedirs(checkpoint_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training running on target device: {device}")

    # Load dataloaders
    train_loader, val_loader, num_classes = get_data_loaders(data_dir)
    
    # Load model architecture
    model = get_model(model_name, num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr)

    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        # 2a. Training Stage
        model.train()
        running_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            
        epoch_loss = running_loss / len(train_loader.dataset)

        # 2b. Validation Stage
        model.eval()
        val_loss = 0.0
        correct = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)
                
                _, preds = torch.max(outputs, 1)
                correct += torch.sum(preds == labels.data)

        epoch_val_loss = val_loss / len(val_loader.dataset)
        val_acc = correct.double() / len(val_loader.dataset)

        print(f"Epoch {epoch}/{epochs} | Train Loss: {epoch_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | Val Acc: {val_acc:.4f}")

        # 2c. Checkpointing & Auto-Save (Transformer Pattern)
        # Always save the latest epoch checkpoint to support recovery
        latest_checkpoint_path = os.path.join(checkpoint_dir, "checkpoint-latest.pt")
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss': epoch_val_loss,
        }, latest_checkpoint_path)

        # Save Best Model explicitly if validation loss improves
        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            best_model_path = os.path.join(checkpoint_dir, "best-model")
            os.makedirs(best_model_path, exist_ok=True)
            
            # Save weights state dictionary
            torch.save(model.state_dict(), os.path.join(best_model_path, "pytorch_model.bin"))
            # Save model config metadata
            with open(os.path.join(best_model_path, "config.txt"), "w") as f:
                f.write(f"model_type: {model_name}\nnum_classes: {num_classes}\nval_loss: {best_val_loss:.4f}\n")
            print(f"[+] Validation loss improved. Best model autosaved to: {best_model_path}")

if __name__ == "__main__":
    train_model(model_name="efficientnet", data_dir="data/processed", epochs=15)
```

---

## 3. Metric Evaluation Script (`src/evaluate.py`)

Generates classification assessments: **Accuracy**, **Precision**, **Recall**, and **F1-Score**.

```python
# training/evaluate.py
import torch
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from models import get_model

def evaluate_best_model(model_name, data_dir, model_weights_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    test_dataset = datasets.ImageFolder(f"{data_dir}/test", transform=transform)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    model = get_model(model_name, len(test_dataset.classes))
    model.load_state_dict(torch.load(model_weights_path, map_location=device))
    model.to(device)
    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    # Calculate metrics using scikit-learn
    acc = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='weighted')

    print("\n" + "="*30)
    print("      EVALUATION METRICS      ")
    print("="*30)
    print(f"Accuracy:  {acc*100:.2f}%")
    print(f"Precision: {precision*100:.2f}%")
    print(f"Recall:    {recall*100:.2f}%")
    print(f"F1-Score:  {f1*100:.2f}%")
    print("="*30)

if __name__ == "__main__":
    evaluate_best_model(
        model_name="efficientnet", 
        data_dir="data/processed", 
        model_weights_path="checkpoints/best-model/pytorch_model.bin"
    )
```

---

## 4. Single-Image Inference Script (`src/predict.py`)

Runs real-time prediction locally or returns raw classifications inside API loops.

```python
# training/predict.py
import torch
import torchvision.transforms as transforms
from PIL import Image
from models import get_model

def predict_single_image(model_name, num_classes, model_weights_path, image_path, class_names):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Preprocess image
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device) # Add batch dimension

    # Load Model
    model = get_model(model_name, num_classes)
    model.load_state_dict(torch.load(model_weights_path, map_location=device))
    model.to(device)
    model.eval()

    # Predict
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        conf, class_idx = torch.max(probabilities, dim=0)
        
    detected_class = class_names[class_idx.item()]
    confidence_score = conf.item()

    print(f"[*] Inference Result: Class: {detected_class} | Confidence: {confidence_score*100:.2f}%")
    return detected_class, confidence_score

if __name__ == "__main__":
    classes = ["Tomato_Blight", "Tomato_Healthy", "Coffee_Rust", "Coffee_Healthy"]
    predict_single_image(
        model_name="efficientnet",
        num_classes=4,
        model_weights_path="checkpoints/best-model/pytorch_model.bin",
        image_path="test_leaf.jpg",
        class_names=classes
    )
```

---

*This Deep Learning framework enables model selection, automated execution on GPU devices, dynamic checkpoints, validation auto-saving, and evaluation.*
