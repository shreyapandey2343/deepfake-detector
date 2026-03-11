import os
import shutil
import random

SOURCE_DIR = "data_subset"
TARGET_DIR = "data"

SPLIT_RATIO = 0.8  # 80% train, 20% val

CLASSES = ["real", "fake"]

random.seed(42)

for cls in CLASSES:
    src_path = os.path.join(SOURCE_DIR, cls)
    images = os.listdir(src_path)
    random.shuffle(images)

    split_idx = int(len(images) * SPLIT_RATIO)

    train_imgs = images[:split_idx]
    val_imgs = images[split_idx:]

    train_dir = os.path.join(TARGET_DIR, "train", cls)
    val_dir = os.path.join(TARGET_DIR, "val", cls)

    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)

    for img in train_imgs:
        shutil.copy(
            os.path.join(src_path, img),
            os.path.join(train_dir, img)
        )

    for img in val_imgs:
        shutil.copy(
            os.path.join(src_path, img),
            os.path.join(val_dir, img)
        )

print("Dataset split completed successfully.")
