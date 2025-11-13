import os
os.environ['KERAS_BACKEND'] = 'jax'
import warnings
warnings.filterwarnings('ignore')
import cv2
import numpy as np
from live_sign_detect import Detector
import time

try:
    import pyttsx3
    VOICE_AVAILABLE = True
except:
    VOICE_AVAILABLE = False

class LiveSignDetector:
    def __init__(self):
        self.detector = Detector()
        self.engine = None
        if VOICE_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.9)
            except:
                self.engine = None
        self.last_spoken = None
        self.last_speak_time = 0
        self.speak_cooldown = 2.0
        self.show_subtitles = True
        self.voice_enabled = True
        self.detection_count = 0
        self.fps = 0
        self.fps_time = time.time()
        self.fps_counter = 0
        self.color_bg = (240, 240, 240)
        self.color_primary = (200, 100, 50)
        self.color_success = (50, 200, 100)
        self.color_text = (50, 50, 50)
        self.color_overlay = (0, 0, 0)
        
    def speak(self, text):
        if not self.voice_enabled or not self.engine:
            return
        current_time = time.time()
        if text != self.last_spoken or (current_time - self.last_speak_time) > self.speak_cooldown:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                self.last_spoken = text
                self.last_speak_time = current_time
            except:
                pass
    
    def draw_ui(self, frame, label, confidence):
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0, 0), (w, 60), self.color_primary, -1)
        cv2.putText(frame, "LIVE SIGN LANGUAGE DETECTION", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        fps_text = f"FPS: {self.fps}"
        cv2.putText(frame, fps_text, (w - 150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if label and confidence > 0.5:
            if self.show_subtitles:
                box_h = 120
                cv2.rectangle(frame, (0, h - box_h), (w, h), (0, 0, 0), -1)
                cv2.rectangle(frame, (0, h - box_h), (w, h), self.color_success, 3)
                text = f"{label}"
                font_scale = 2.5
                thickness = 4
                (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_BOLD, font_scale, thickness)
                text_x = (w - text_w) // 2
                text_y = h - box_h + 60
                cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_BOLD, font_scale, self.color_success, thickness)
                conf_text = f"Confidence: {confidence:.1%}"
                cv2.putText(frame, conf_text, ((w - 250) // 2, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
            self.detection_count += 1
        panel_w = 250
        panel_h = 180
        panel_x = 20
        panel_y = 80
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (255, 255, 255), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), self.color_primary, 2)
        y_offset = panel_y + 35
        line_h = 35
        cv2.putText(frame, "STATISTICS", (panel_x + 10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color_text, 2)
        cv2.putText(frame, f"Detections: {self.detection_count}", (panel_x + 10, y_offset + line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_text, 1)
        cv2.putText(frame, f"Subtitles: {'ON' if self.show_subtitles else 'OFF'}", (panel_x + 10, y_offset + 2*line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_text, 1)
        cv2.putText(frame, f"Voice: {'ON' if self.voice_enabled else 'OFF'}", (panel_x + 10, y_offset + 3*line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_text, 1)
        controls = ["CONTROLS:", "Q - Quit", "S - Subtitles", "V - Voice"]
        ctrl_x = w - 180
        ctrl_y = h - 150
        for i, text in enumerate(controls):
            color = (255, 255, 255) if i == 0 else (200, 200, 200)
            weight = 2 if i == 0 else 1
            cv2.putText(frame, text, (ctrl_x, ctrl_y + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, weight)
        return frame
    
    def update_fps(self):
        self.fps_counter += 1
        if self.fps_counter >= 10:
            current_time = time.time()
            elapsed = current_time - self.fps_time
            self.fps = int(self.fps_counter / elapsed)
            self.fps_counter = 0
            self.fps_time = current_time
    
    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cv2.namedWindow('Sign Language Detection', cv2.WINDOW_NORMAL)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
                label, confidence, annotated = self.detector.predict(frame)
                frame_ui = self.draw_ui(annotated, label, confidence)
                if label and confidence > 0.7:
                    self.speak(label)
                self.update_fps()
                cv2.imshow('Sign Language Detection', frame_ui)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('s') or key == ord('S'):
                    self.show_subtitles = not self.show_subtitles
                elif key == ord('v') or key == ord('V'):
                    self.voice_enabled = not self.voice_enabled
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == '__main__':
    app = LiveSignDetector()
    app.run()
