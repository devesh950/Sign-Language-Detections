# 🤟 Sign Language Detection

ASL gesture recognition using MediaPipe and Neural Networks.

## 📁 Essential Files

### 1. Live Camera (LOCAL ONLY) ✅
**File:** `live_sign_detect.py`
```bash
python live_sign_detect.py
```
- Real-time webcam detection
- Fastest performance
- **Cannot deploy to cloud** (needs physical camera)

### 2. Photo Upload (CAN DEPLOY) ✅
**File:** `streamlit_app.py`
```bash
streamlit run streamlit_app.py
```
- Upload photos of hand gestures
- Deploy to Streamlit Cloud
- No live camera needed

### 3. Training Files
- `capture_images.py` - Capture training images
- `extract_landmarks.py` - Extract hand landmarks
- `train_model.py` - Train neural network
- `sign_model.h5` - Trained model (37 gestures)
- `labels.pkl` - Gesture labels

## 🚀 Quick Start

### Install Dependencies
```bash
pip install opencv-python mediapipe keras numpy pandas scikit-learn streamlit pyttsx3
```

### Run Live Detection
```bash
python live_sign_detect.py
```
**Controls:**
- `q` = Quit
- `s` = Toggle subtitles
- `v` = Toggle voice

### Run Photo Upload
```bash
streamlit run streamlit_app.py
```

## 🎯 Gestures

- **Letters:** A-Z (26)
- **Numbers:** 0-9 (10)
- **Special:** Space (1)
- **Total:** 37 gestures

## 🌐 Deployment

### ❌ Cannot Deploy Live Camera
Cloud servers (Render, Heroku, etc.) have no physical webcam.

### ✅ Can Deploy Photo Upload
Deploy `streamlit_app.py` to:
- Streamlit Cloud (free)
- Heroku
- AWS/Azure/GCP

## 📝 License

MIT License
