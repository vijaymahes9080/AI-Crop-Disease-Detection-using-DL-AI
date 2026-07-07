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
