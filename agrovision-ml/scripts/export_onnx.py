# scripts/export_onnx.py
import torch
import argparse
from training.models import get_model

def export_to_onnx(model_name, weights_path, num_classes, output_path):
    print(f"[*] Loading PyTorch model '{model_name}' for ONNX export...")
    device = torch.device("cpu") # Export on CPU for clean static graph paths
    
    # Load model and apply state dictionary weights
    model = get_model(model_name, num_classes, pretrained=False)
    model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()

    # Create standard dummy input matching crop resolution
    dummy_input = torch.randn(1, 3, 224, 224)

    # Export graph
    print(f"[*] Compiling computational graph to: {output_path}...")
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=15, # Enforces modern operations compatibility
        do_constant_folding=True,
        input_names=["input_tensor"],
        output_names=["output_logits"],
        dynamic_axes={
            "input_tensor": {0: "batch_size"}, # Allows dynamic batch sizes
            "output_logits": {0: "batch_size"}
        }
    )
    print("[+] Model exported to ONNX successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights_path", default="checkpoints/best-model/pytorch_model.bin")
    parser.add_argument("--output_path", default="checkpoints/crop_disease.onnx")
    parser.add_argument("--num_classes", type=int, default=4)
    args = parser.parse_args()
    export_to_onnx("efficientnet", args.weights_path, args.num_classes, args.output_path)
