# scripts/convert_tflite.py
import tensorflow as tf
import numpy as np
import argparse
import os

# 1. Representative Data Generator (Calibrates weight mapping parameters)
def representative_data_gen(dataset_dir="data/processed/val", num_samples=100):
    # Crawl directories to load valid crop leaves
    image_paths = []
    for root, _, files in os.walk(dataset_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_paths.append(os.path.join(root, file))
    
    # Draw sample batch
    sample_paths = np.random.choice(image_paths, size=min(num_samples, len(image_paths)), replace=False)
    
    for path in sample_paths:
        # Load and resize to target model dims
        img = tf.keras.preprocessing.image.load_img(path, target_size=(224, 224))
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        # Normalize matching ImageNet standard configuration
        img_array = (img_array / 255.0 - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        img_tensor = np.expand_dims(img_array, axis=0).astype(np.float32)
        yield [img_tensor]

def convert_to_tflite(onnx_path, output_tflite_path):
    # Note: Intermediate step requires building the SavedModel graph via onnx-tf
    # pip install onnx-tf (Assumed compiled folder: 'checkpoints/saved_model')
    print("[*] Converting ONNX graph to SavedModel structures...")
    os.system(f"onnx-tf convert -i {onnx_path} -o checkpoints/saved_model")
    
    print("[*] Launching TensorFlow Lite INT8 Quantization...")
    converter = tf.lite.TFLiteConverter.from_saved_model("checkpoints/saved_model")
    
    # Enforce optimization policies
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_data_gen
    
    # Strict full integer operations conversion policy
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    # Enforce input and output nodes to INT8 representation (removes float wrapper)
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_quant_model = converter.convert()
    
    # Save optimized weights
    with open(output_tflite_path, "wb") as f:
        f.write(tflite_quant_model)
    print(f"[+] Full Integer Quantized model saved to: {output_tflite_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--onnx_path", default="checkpoints/crop_disease.onnx")
    parser.add_argument("--output_path", default="checkpoints/crop_disease_quant.tflite")
    args = parser.parse_args()
    convert_to_tflite(args.onnx_path, args.output_path)
