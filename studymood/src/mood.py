import cv2
import numpy as np

class MoodDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    def detect_mood(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        mood = "Neutral"
        focus = 0

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            if len(smiles) > 0:
                mood = "Happy"
            else:
                mood = "Serious"
            focus = 1  # face is visible → focused
            break

        return mood, focus
