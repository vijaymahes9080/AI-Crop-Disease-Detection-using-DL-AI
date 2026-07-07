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
