#!/bin/bash
# agrovision-ml/scripts/package_mar.sh
# Packages the PyTorch models into a TorchServe .mar archive

echo "[*] Packaging AgroVision Model into MAR archive..."

# Ensure we are in the correct directory (agrovision-ml)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Create output folder if not exists
mkdir -p model_store

# Run torch-model-archiver
# Note: In production, ensure torch-model-archiver is installed via pip
torch-model-archiver \
  --model-name crop_disease \
  --version 1.0 \
  --model-file training/models.py \
  --serialized-file checkpoints/checkpoint-latest.pt \
  --handler inference/custom_handler.py \
  --export-path model_store \
  --force

echo "[+] Model archive packaged successfully at model_store/crop_disease.mar"
