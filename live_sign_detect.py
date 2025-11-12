# Set Keras backend to JAX before importing keras
import os
os.environ['KERAS_BACKEND'] = 'jax'

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

import cv2
import mediapipe as mp
import numpy as np
import keras
import pickle
import time
from collections import deque, Counter


class Detector:
    """Hand sign detector wrapper.

    Usage:
      detector = Detector(model_path='sign_model.h5', labels_path='labels.pkl')
      label, conf, annotated = detector.predict(frame_bgr)

    The class is safe to import (it won't open the webcam). The module also
    contains a small CLI when run directly that starts the webcam and uses
    pyttsx3 to speak predictions.
    """

    def __init__(self, model_path='sign_model.h5', labels_path='labels.pkl',
                 buffer_len=5, min_detection_confidence=0.7, min_tracking_confidence=0.7):
        self.model = keras.models.load_model(model_path)
        with open(labels_path, 'rb') as f:
            self.le = pickle.load(f)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1, 
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.buffer = deque(maxlen=buffer_len)

    @staticmethod
    def _normalize(lms):
        pts = np.array([[p.x, p.y, p.z] for p in lms], dtype=np.float32)
        wrist = pts[0]
        pts -= wrist
        scale = np.max(np.linalg.norm(pts, axis=1))
        if scale > 0:
            pts /= scale
        return pts.flatten()

    def predict(self, frame_bgr):
        """Run detection on a BGR OpenCV frame.

        Returns: (label_or_None, confidence_float, annotated_frame)
        If no hand detected, label is None and annotated_frame is original frame.
        """
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)

        if not res.multi_hand_landmarks:
            return None, 0.0, frame_bgr

        lm = res.multi_hand_landmarks[0]
        vec = self._normalize(lm.landmark).reshape(1, -1)
        pred = self.model.predict(vec, verbose=0)[0]
        idx = int(np.argmax(pred))
        label = self.le.inverse_transform([idx])[0]
        conf = float(pred[idx])
        self.buffer.append(label)
        common = Counter(self.buffer).most_common(1)[0][0]

        annotated = frame_bgr.copy()
        self.mp_draw.draw_landmarks(annotated, lm, self.mp_hands.HAND_CONNECTIONS)
        text = f"{common} ({conf:.2f})"
        cv2.putText(annotated, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        return common, conf, annotated


if __name__ == '__main__':
    # Backwards-compatible CLI that uses the webcam and speaks results.
    try:
        import pyttsx3
    except Exception:
        pyttsx3 = None

    detector = Detector()
    engine = None
    if pyttsx3:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)

    last_spoken, last_time = None, 0

    cap = cv2.VideoCapture(0)
    print("Press ESC to quit")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        label, conf, annotated = detector.predict(frame)

        if label and conf > 0.7 and label != last_spoken and (time.time() - last_time) > 1.5:
            if engine:
                engine.say(label)
                engine.runAndWait()
            last_spoken = label
            last_time = time.time()

        display = annotated if annotated is not None else frame
        cv2.imshow('Live Sign Detection', display)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
