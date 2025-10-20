import cv2
import numpy as np

class MoodDetector:
    def __init__(self):
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")
            self.cascade_loaded = True
        except Exception as e:
            self.cascade_loaded = False
            print(f"Cascade classifiers not available: {e}")

    def detect_mood(self, frame):
        mood = "Neutral"
        focus = 0.5  # Default focus when no camera
        
        if self.cascade_loaded and frame is not None and frame.size > 0 and np.mean(frame) > 0:
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
                    if len(smiles) > 0:
                        mood = "Happy"
                    else:
                        mood = "Serious"
                    focus = 0.8  # Face detected → higher focus
                    break
                    
            except Exception as e:
                # If face detection fails, use default values
                print(f"Face detection error: {e}")
        
        return mood, focus
