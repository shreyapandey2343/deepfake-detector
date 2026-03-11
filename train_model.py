from tensorflow.keras.applications.efficientnet import preprocess_input
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# -----------------------------
# CONFIG (LOCKED)
# -----------------------------
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
LR = 1e-5

TRAIN_DIR = "data/train"
VAL_DIR = "data/val"

# -----------------------------
# DATA GENERATORS (CORRECT)
# -----------------------------
train_gen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=10,
    width_shift_range=0.05,
    height_shift_range=0.05,
    brightness_range=[0.8, 1.2],
    zoom_range=0.1,
    horizontal_flip=True
)

val_gen = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

train_data = train_gen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

print("Class indices:", train_data.class_indices)
# expected: {'fake': 0, 'real': 1}

val_data = val_gen.flow_from_directory(
    VAL_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode="binary"
)

# -----------------------------
# MODEL
# -----------------------------
base_model = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Freeze most of the backbone (STABLE)
for layer in base_model.layers[:-40]:
    layer.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation="relu")(x)
x = Dropout(0.5)(x)
output = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=output)

# -----------------------------
# COMPILE (STABLE)
# -----------------------------
model.compile(
    optimizer=Adam(learning_rate=LR),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# -----------------------------
# CLASS WEIGHTS (BIAS FIX)
# -----------------------------
# fake = 0, real = 1
class_weights = {
    0: 1.0,  # fake
    1: 1.3   # real
}

# -----------------------------
# TRAIN
# -----------------------------
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=EPOCHS,
    class_weight=class_weights
)

# -----------------------------
# SAVE (FINAL)
# -----------------------------
model.save("models/eagleeye_phase1.h5")
