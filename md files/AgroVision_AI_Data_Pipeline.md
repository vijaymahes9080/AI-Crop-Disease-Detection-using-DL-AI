# Data Pipeline & Processing Infrastructure Spec
## Project: AgroVision AI — Crop Disease Detection Platform

---

## 1. Pipeline Folder Structure

The machine learning data pipeline structures raw intake data into versioned, partitioned datasets.

```
agrovision-pipeline/
├── data/
│   ├── raw/                         # Immutable raw downloads (PlantVillage)
│   ├── intermediate/                # Cleaned & resized image sets
│   └── processed/                   # Final partitions (Train/Val/Test)
│       ├── train/
│       ├── val/
│       └── test/
├── config/
│   └── pipeline_config.yaml         # Augmentation thresholds, image sizes
├── src/
│   ├── clean.py                     # Image sanitization & extension verifier
│   ├── split.py                     # 70/15/15 deterministic split script
│   └── preprocess.py                # Albumentations pipelines & norm calculators
├── dvc.yaml                         # Data Version Control pipeline steps
└── Makefile                         # Shell automation script
```

---

## 2. Python Processing & Preprocessing Scripts

### 2.1 Cleaning Script: `src/clean.py`
This script checks all images, deletes corrupted files, enforces standard extension types, and strips metadata headers.

```python
# src/clean.py
import os
import argparse
from PIL import Image

def clean_dataset(raw_dir, target_dir):
    print(f"[*] Sanitizing datasets from '{raw_dir}' into '{target_dir}'...")
    supported_formats = {'.jpg', '.jpeg', '.png'}
    corrupt_count = 0
    clean_count = 0

    for root, _, files in os.walk(raw_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in supported_formats:
                continue

            file_path = os.path.join(root, file)
            try:
                # Open image and verify structure integrity
                with Image.open(file_path) as img:
                    img.verify()
                
                # Re-open to convert and strip EXIF profile metadata
                with Image.open(file_path) as img:
                    img_rgb = img.convert("RGB")
                    
                    # Create structural replica target path
                    rel_path = os.path.relpath(root, raw_dir)
                    dest_folder = os.path.join(target_dir, rel_path)
                    os.makedirs(dest_folder, exist_ok=True)
                    
                    dest_file_path = os.path.join(dest_folder, os.path.splitext(file)[0] + ".jpg")
                    img_rgb.save(dest_file_path, "JPEG", quality=95)
                    clean_count += 1
            except Exception as e:
                print(f"[!] Defective image detected and removed: {file_path}. Reason: {e}")
                corrupt_count += 1

    print(f"[+] Completed: Cleaned {clean_count} images. Discarded {corrupt_count} corrupt files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", default="data/raw")
    parser.add_argument("--target_dir", default="data/intermediate")
    args = parser.parse_args()
    clean_dataset(args.raw_dir, args.target_dir)
```

---

### 2.2 Split Script: `src/split.py`
Splits dataset folders deterministically into **Train (70%)**, **Validation (15%)**, and **Test (15%)** directories.

```python
# src/split.py
import os
import shutil
import random
import argparse

def split_dataset(src_dir, dest_dir, seed=42):
    random.seed(seed)
    train_pct, val_pct, test_pct = 0.70, 0.15, 0.15
    print(f"[*] Splitting dataset: {src_dir} -> {dest_dir} (Seed: {seed})...")

    # Clean existing target directories
    for p in ['train', 'val', 'test']:
        path = os.path.join(dest_dir, p)
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)

    # Walk classes (subdirectories representing categories)
    for category in os.listdir(src_dir):
        cat_path = os.path.join(src_dir, category)
        if not os.path.isdir(cat_path):
            continue

        images = [f for f in os.listdir(cat_path) if os.path.isfile(os.path.join(cat_path, f))]
        random.shuffle(images)

        total_imgs = len(images)
        train_idx = int(total_imgs * train_pct)
        val_idx = train_idx + int(total_imgs * val_pct)

        partitions = {
            'train': images[:train_idx],
            'val': images[train_idx:val_idx],
            'test': images[val_idx:]
        }

        for subset, img_list in partitions.items():
            dest_subset_dir = os.path.join(dest_dir, subset, category)
            os.makedirs(dest_subset_dir, exist_ok=True)
            for img in img_list:
                shutil.copy2(
                    os.path.join(cat_path, img),
                    os.path.join(dest_subset_dir, img)
                )

    print("[+] Dataset splitting complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_dir", default="data/intermediate")
    parser.add_argument("--dest_dir", default="data/processed")
    args = parser.parse_args()
    split_dataset(args.src_dir, args.dest_dir)
```

---

### 2.3 Preprocessing & Augmentation Pipeline: `src/preprocess.py`
Leverages `Albumentations` to apply spectral, spatial, and light-variance alterations simulating field phone capture issues.

```python
# src/preprocess.py
import albumentations as A
import cv2
import os
import argparse
import numpy as np

def get_train_pipeline(img_size=224):
    return A.Compose([
        A.Resize(img_size, img_size),
        A.HorizontalFlip(p=0.5),
        A.RandomRotate90(p=0.5),
        A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.15, rotate_limit=30, border_mode=cv2.BORDER_CONSTANT, p=0.7),
        # Simulate field lighting and shadows
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        A.RandomShadow(p=0.3),
        # Simulate camera noise
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
        A.Blur(blur_limit=3, p=0.2)
    ])

def process_and_augment(input_dir, size=224):
    print(f"[*] Running data augmentation on training set...")
    transform = get_train_pipeline(size)
    train_dir = os.path.join(input_dir, "train")

    for root, _, files in os.walk(train_dir):
        for file in files:
            file_path = os.path.join(root, file)
            image = cv2.imread(file_path)
            if image is None:
                continue

            # Run 2 augmentations per raw file to double training data
            for i in range(2):
                augmented = transform(image=image)
                aug_image = augmented['image']
                
                # Save augmented replica
                filename, ext = os.path.splitext(file)
                new_filename = f"{filename}_aug_{i}{ext}"
                cv2.imwrite(os.path.join(root, new_filename), aug_image)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="data/processed")
    parser.add_argument("--img_size", type=int, default=224)
    args = parser.parse_args()
    process_and_augment(args.input_dir, args.img_size)
```

---

## 3. Data Version Control (DVC) Pipeline Setup

To keep massive training image files out of Git version logs while ensuring training reproducibility, we configure **DVC (Data Version Control)**.

### 3.1 DVC Stage Definitions (`dvc.yaml`)
Create this file in the project root to map stage inputs, outputs, and script triggers.

```yaml
stages:
  clean:
    cmd: python src/clean.py --raw_dir data/raw --target_dir data/intermediate
    deps:
      - data/raw
      - src/clean.py
    outs:
      - data/intermediate

  split:
    cmd: python src/split.py --src_dir data/intermediate --dest_dir data/processed
    deps:
      - data/intermediate
      - src/split.py
    outs:
      - data/processed

  preprocess:
    cmd: python src/preprocess.py --input_dir data/processed --img_size 224
    deps:
      - data/processed
      - src/preprocess.py
```

---

## 4. Pipeline Automation

### Makefile Configuration
Create this file to orchestrate pipeline initialization and execution steps cleanly.

```makefile
# Orchestrates execution commands for pipelines
.PHONY: init run status clean

init:
	@echo "Initializing DVC storage..."
	pip install -r requirements.txt
	dvc init
	# Configure local drive or cloud S3 as remote data store
	dvc remote add -d myremote /tmp/dvc-storage

run:
	@echo "Executing pipeline stages..."
	dvc repro

status:
	@echo "Comparing pipeline modifications..."
	dvc status

clean:
	@echo "Resetting pipeline directories..."
	rm -rf data/intermediate data/processed
	dvc gc -f
```

---

*This data pipeline blueprint enables reproducible data sanitization, partitioning, and robust data versioning control on the AgroVision AI platform.*
