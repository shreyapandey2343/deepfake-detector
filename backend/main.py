# ===== Imports =====

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import sqlite3
import hashlib
import io
import os
from tensorflow.keras.applications.efficientnet import preprocess_input


# ===== TensorFlow Memory Optimization =====
# Reduces TensorFlow memory usage on small servers like Render

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)


# ===== App Initialization =====

app = FastAPI(title="EagleEye Deepfake Detector")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")),
    name="static"
)


# ===== Serve Frontend Pages =====

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/login")
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))


# ===== CORS =====

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Database Setup (SQLite) =====

conn = sqlite3.connect("auth.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    prediction TEXT,
    confidence REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# ===== Utility Functions =====

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# ===== Authentication Routes =====

@app.post("/signup")
def signup(email: str = Form(...), password: str = Form(...)):

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hash_password(password))
        )

        conn.commit()

        return {"status": "ok"}

    except:
        return {"status": "error", "message": "User already exists"}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):

    cursor.execute(
        "SELECT role FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )

    user = cursor.fetchone()

    if user:
        return {"status": "ok", "role": user[0]}

    return {"status": "error", "message": "Invalid credentials"}


# ===== ML Helpers =====

IMG_SIZE = 224
FAKE_THRESHOLD = 0.55
REAL_THRESHOLD = 0.45

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_face(image: Image.Image):

    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(30, 30)
    )

    return faces


def is_too_dark(image: Image.Image):

    gray = np.array(image.convert("L"))
    return gray.mean() < 40


def prepare_image(image: Image.Image):

    image = image.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr = np.expand_dims(np.array(image), axis=0)

    return preprocess_input(arr)


# ===== Model Loading (Lazy Load) =====

MODEL_PATH = os.path.join(BASE_DIR, "models", "eagleeye_phase1.h5")

model = None


def get_model():
    global model

    if model is None:
        print("Loading model...")
        model = tf.keras.models.load_model(MODEL_PATH, compile=False)

    return model


# ===== Prediction Route =====

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()

    try:
        image = Image.open(io.BytesIO(contents))
    except:
        return {"error": "Invalid input image"}

    try:

        faces = detect_face(image)

        # Reject images with no face OR extremely dark
        if len(faces) == 0 or is_too_dark(image):
            return {"error": "Invalid input image"}

        # Crop first detected face
        x, y, w, h = faces[0]

        img_np = np.array(image.convert("RGB"))
        face = img_np[y:y+h, x:x+w]

        face_img = Image.fromarray(face)

        img = prepare_image(face_img)

        model = get_model()

        prob = float(model.predict(img)[0][0])

        if prob >= FAKE_THRESHOLD:
            label = "Fake"

        elif prob <= REAL_THRESHOLD:
            label = "Real"

        else:
            label = "Uncertain"

        return {
            "prediction": label,
            "confidence": round(prob, 3)
        }

    except Exception as e:
        print("Prediction error:", e)
        return {"error": "Prediction failed"}