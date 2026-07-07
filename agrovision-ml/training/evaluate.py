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
