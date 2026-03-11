import os
import cv2

REAL_VIDEO_SOURCE = "data/raw"
REAL_OUTPUT_DIR = "data/real"

os.makedirs(REAL_OUTPUT_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

for root, _, files in os.walk(REAL_VIDEO_SOURCE):
    for file in files:
        if file.endswith(".mp4") and "manipulated" not in root.lower():
            video_path = os.path.join(root, file)
            cap = cv2.VideoCapture(video_path)

            frame_count = 0
            success = True
            video_name = os.path.splitext(file)[0]

            while success:
                success, frame = cap.read()
                if not success:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    face = frame[y:y+h, x:x+w]
                    face = cv2.resize(face, (224, 224))
                    img_name = f"{video_name}_{frame_count}.jpg"
                    cv2.imwrite(os.path.join(REAL_OUTPUT_DIR, img_name), face)
                    frame_count += 1

            cap.release()
            print(f"Extracted {frame_count} real faces from {file}")
