# serve/handlers/crop_classifier_handler.py
import io
import torch
import torchvision.transforms as transforms
from PIL import Image
from ts.torch_handler.image_classifier import ImageClassifier

class CropClassifierHandler(ImageClassifier):
    def __init__(self):
        super(CropClassifierHandler, self).__init__()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def preprocess(self, data):
        images = []
        for row in data:
            image_data = row.get("data") or row.get("body")
            if isinstance(image_data, str):
                # Handle base64 encoded string
                import base64
                image_data = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image_tensor = self.transform(image)
            images.append(image_tensor)
        return torch.stack(images).to(self.device)

    def inference(self, model_input):
        with torch.no_grad():
            outputs = self.model(model_input)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            return probabilities

    def postprocess(self, inference_output):
        # Maps model logits back to plant disease mappings
        results = []
        for probs in inference_output:
            top_prob, top_idx = torch.max(probs, dim=0)
            results.append({
                "class_id": int(top_idx),
                "confidence": float(top_prob)
            })
        return results
