import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.efficientnet import preprocess_input
from sklearn.metrics import classification_report, confusion_matrix

IMG_SIZE = (224, 224)
BATCH_SIZE = 8
DATA_DIR = "data_subset"
MODEL_PATH = "models/deepfake_model.h5"

# Load model
model = load_model(MODEL_PATH)

# Data generator
datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    validation_split=0.2
)

val_data = datagen.flow_from_directory(
    DATA_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode="binary",
    subset="validation",
    shuffle=False
)

# IMPORTANT FIX
val_data.reset()

# Predict probabilities
y_prob = model.predict(
    val_data,
    steps=len(val_data),
    verbose=1
)

# Threshold tuning (accuracy-oriented)
THRESHOLD = 0.6
y_pred = (y_prob > THRESHOLD).astype(int).ravel()

# True labels
y_true = val_data.classes

# Evaluation
print("\nClassification Report:\n")
print(classification_report(y_true, y_pred, target_names=["Fake", "Real"]))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_true, y_pred))
