import os
import cv2

RAW_DATA = "data/raw"
REAL_DIR = "data/real"
FAKE_DIR = "data/fake"

os.makedirs(REAL_DIR, exist_ok=True)
os.makedirs(FAKE_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

for root, dirs, files in os.walk(RAW_DATA):
    for file in files:
        if file.endswith(".mp4"):
            video_path = os.path.join(root, file)
            cap = cv2.VideoCapture(video_path)

            label = "fake" if "manipulated" in video_path.lower() else "real"
            save_dir = FAKE_DIR if label == "fake" else REAL_DIR

            frame_count = 0
            success = True

            while success:
                success, frame = cap.read()
                if not success:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = frame[y:y+h, x:x+w]
                    face = cv2.resize(face, (224, 224))
                    img_name = f"{os.path.splitext(file)[0]}_{frame_count}.jpg"
                    cv2.imwrite(os.path.join(save_dir, img_name), face)
                    frame_count += 1

            cap.release()
            print(f"Extracted {frame_count} faces from {file}")
