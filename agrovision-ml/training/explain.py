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
