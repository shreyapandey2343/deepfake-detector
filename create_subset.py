import os
import shutil
import random

SOURCE_REAL = "data/real"
SOURCE_FAKE = "data/fake"

TARGET_REAL = "data_subset/real"
TARGET_FAKE = "data_subset/fake"

NUM_IMAGES = 5000  # per class

os.makedirs(TARGET_REAL, exist_ok=True)
os.makedirs(TARGET_FAKE, exist_ok=True)

def copy_random_images(src, dst, n):
    images = []
    for root, _, files in os.walk(src):
        for f in files:
            if f.lower().endswith((".jpg", ".png", ".jpeg")):
                images.append(os.path.join(root, f))

    selected = random.sample(images, n)

    for img in selected:
        shutil.copy(img, dst)

    print(f"Copied {n} images to {dst}")

copy_random_images(SOURCE_REAL, TARGET_REAL, NUM_IMAGES)
copy_random_images(SOURCE_FAKE, TARGET_FAKE, NUM_IMAGES)
