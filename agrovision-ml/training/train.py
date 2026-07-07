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
