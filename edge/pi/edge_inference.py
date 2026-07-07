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
