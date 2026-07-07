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
