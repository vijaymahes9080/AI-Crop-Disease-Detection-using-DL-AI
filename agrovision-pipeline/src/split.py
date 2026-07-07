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
