# Deep Learning Edge Optimization Spec
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. PyTorch to ONNX Export Script (`scripts/export_onnx.py`)

This script exports a trained PyTorch state dictionary to standard ONNX intermediate representation format with dynamic batch dimensions.

```python
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
```

---

## 2. TensorFlow Lite (TFLite) INT8 Quantization Script (`scripts/convert_tflite.py`)

Compiling to INT8 requires calibration data to map activations from float ranges to 8-bit integers. This script runs **Post-Training Full-Integer Quantization (PTQ)**.

```python
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
```

---

## 3. Platform Integration & Deployment Configurations

### 3.1 Android Integration Code Pattern (Kotlin Task API)
Integrates the quantized TFLite model inside Android modules, enforcing hardware acceleration (NNAPI).

```kotlin
// android/app/src/main/java/ai/agrovision/scanner/CropScanner.kt
package ai.agrovision.scanner

import android.content.Context
import android.graphics.Bitmap
import org.tensorflow.lite.DataType
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import java.io.FileInputStream
import java.nio.channels.FileChannel

class CropScanner(context: Context) {
    private var interpreter: Interpreter

    init {
        // Enforce NNAPI GPU/NPU hardware acceleration delegates
        val options = Interpreter.Options().apply {
            setNumThreads(4)
            useNNAPI = true
        }
        interpreter = Interpreter(loadModelFile(context, "crop_disease_quant.tflite"), options)
    }

    private fun loadModelFile(context: Context, modelPath: String): java.nio.MappedByteBuffer {
        val fileDescriptor = context.assets.openFd(modelPath)
        val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
        val fileChannel = inputStream.channel
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, fileDescriptor.startOffset, fileDescriptor.declaredLength)
    }

    fun scanLeaf(bitmap: Bitmap): Pair<Int, Float> {
        // Preprocess Bitmap image to INT8 normalized format
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(224, 224, ResizeOp.Method.BILINEAR))
            .add(NormalizeOp(floatArrayOf(123.675f, 116.28f, 103.53f), floatArrayOf(58.395f, 57.12f, 57.375f)))
            .build()
            
        val tensorImage = TensorImage(DataType.INT8)
        tensorImage.load(bitmap)
        val processedImage = imageProcessor.process(tensorImage)

        // Outputs tensor allocation (1, num_classes)
        val outputBuffer = Array(1) { ByteArray(4) } // Assuming 4 target classes
        
        interpreter.run(processedImage.buffer, outputBuffer)

        // Find highest class logit probability
        val result = outputBuffer[0]
        var maxIdx = 0
        var maxVal = -128.toByte()
        for (i in result.indices) {
            if (result[i] > maxVal) {
                maxVal = result[i]
                maxIdx = i
            }
        }
        // Dequantize logic: (value - zero_point) * scale
        val confidence = (maxVal.toFloat() + 128f) / 255.0f
        return Pair(maxIdx, confidence)
    }
}
```

---

### 3.2 Raspberry Pi Integration (Python Edge Run Script)
Executes edge predictions on low-resource ARM chips without full TensorFlow dependency installations.

```python
# pi/edge_inference.py
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite

def run_pi_inference(image_path, model_path="crop_disease_quant.tflite"):
    # Load interpreter explicitly targeting ARM Neon optimizations
    interpreter = tflite.Interpreter(model_path=model_path, num_threads=4)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    # Preprocess image conforming to INT8 quantization scales
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img, dtype=np.float32) / 255.0
    # Apply standard mean/std
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    normalized_img = (img_array - mean) / std

    # Quantize inputs: value_quant = (value / scale) + zero_point
    input_scale, input_zero_point = input_details["quantization"]
    quantized_img = (normalized_img / input_scale) + input_zero_point
    quantized_img = np.expand_dims(quantized_img, axis=0).astype(input_details["dtype"])

    # Forward pass execution
    interpreter.set_tensor(input_details["index"], quantized_img)
    interpreter.invoke()

    # Fetch and dequantize output logits
    output_tensor = interpreter.get_tensor(output_details["index"])[0]
    output_scale, output_zero_point = output_details["quantization"]
    dequantized_output = (output_tensor.astype(np.float32) - output_zero_point) * output_scale

    # Compute softmax
    exp_logits = np.exp(dequantized_output - np.max(dequantized_output))
    probabilities = exp_logits / np.sum(exp_logits)

    predicted_idx = np.argmax(probabilities)
    confidence = probabilities[predicted_idx]
    
    print(f"[+] Pi Diagnosis: Class: {predicted_idx} | Confidence: {confidence*100:.2f}%")
    return predicted_idx, confidence
```

---

*This edge optimization deployment specification provides graph conversion scripts, INT8 quantization setups, and mobile/IoT target integration configurations.*
