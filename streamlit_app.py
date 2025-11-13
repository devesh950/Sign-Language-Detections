import os
os.environ['KERAS_BACKEND'] = 'jax'
import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import numpy as np
from PIL import Image
import mediapipe as mp
import keras
import pickle
import pyttsx3
import threading

st.set_page_config(page_title="Sign Language Detection", page_icon="🤟", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    
    * {font-family: 'Poppins', sans-serif;}
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    h1 {
        color: white;
        text-align: center;
        font-size: 56px;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        animation: fadeIn 1s;
    }
    
    h2 {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 24px;
        font-weight: 400;
        margin-bottom: 30px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-size: 20px;
        font-weight: 600;
        padding: 15px 40px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 8px 20px rgba(245,87,108,0.4);
        transition: all 0.3s ease;
        width: 100%;
        margin: 10px 0;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(245,87,108,0.6);
    }
    
    .prediction-box {
        background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 52%, #2BFF88 90%);
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        color: white;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    .prediction-text {
        font-size: 72px;
        font-weight: 700;
        margin: 10px 0;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.4);
    }
    
    .confidence-text {
        font-size: 28px;
        font-weight: 600;
        opacity: 0.95;
    }
    
    .info-card {
        background: rgba(255,255,255,0.95);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }
    
    .subtitle-box {
        background: rgba(0,0,0,0.85);
        color: #2BFF88;
        padding: 20px 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin: 15px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border: 3px solid #2BFF88;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }
    
    .stat-box {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        flex: 1;
        margin: 0 10px;
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    
    @keyframes pulse {
        0%, 100% {transform: scale(1);}
        50% {transform: scale(1.02);}
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True
if 'subtitles_enabled' not in st.session_state:
    st.session_state.subtitles_enabled = True
if 'detection_count' not in st.session_state:
    st.session_state.detection_count = 0
if 'last_gesture' not in st.session_state:
    st.session_state.last_gesture = "None"

@st.cache_resource
def load_model():
    model = keras.models.load_model('sign_model.h5')
    with open('labels.pkl', 'rb') as f:
        le = pickle.load(f)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.7)
    return model, le, hands

def speak_gesture(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    except:
        pass

def predict_gesture(image_pil, model, le, hands):
    img_array = np.array(image_pil)
    if img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    
    res = hands.process(img_array)
    
    if res.multi_hand_landmarks:
        hand_landmarks = res.multi_hand_landmarks[0]
        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        landmarks = np.array(landmarks).reshape(1, -1)
        
        prediction = model.predict(landmarks, verbose=0)
        predicted_class = np.argmax(prediction, axis=1)
        confidence = float(np.max(prediction))
        label = le.inverse_transform(predicted_class)[0]
        
        annotated = img_array.copy()
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_drawing.draw_landmarks(
            annotated,
            hand_landmarks,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )
        
        return label, confidence, Image.fromarray(annotated)
    return None, None, image_pil

st.markdown("<h1>🤟 Sign Language Detection System</h1>", unsafe_allow_html=True)
st.markdown("<h2>Upload Photo for Hand Gesture Recognition with Voice & Subtitles</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    
    st.markdown("#### 🎤 Voice Output")
    st.session_state.voice_enabled = st.toggle("Enable Voice", value=st.session_state.voice_enabled)
    
    st.markdown("#### 💬 Show Gesture")
    st.session_state.subtitles_enabled = st.toggle("Show Detected Gesture", value=st.session_state.subtitles_enabled)
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    st.markdown(f"""
    <div class='info-card'>
        <div class='stat-number'>{st.session_state.detection_count}</div>
        <div class='stat-label'>Detections</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    - **37 Gestures**: A-Z, 0-9, Space
    - **21 Hand Landmarks**
    - **Real-time Detection**
    - **Voice Feedback**
    - **High Accuracy**
    """)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='info-card'><h3 style='color: #667eea; text-align: center;'>� Upload Photo</h3></div>", unsafe_allow_html=True)
    
    uploaded = st.file_uploader("Choose a hand gesture image...", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    
    if uploaded:
        image = Image.open(uploaded)
        st.image(image, caption="Uploaded Image", width=600)
        
        with st.spinner('Detecting gesture...'):
            model, le, hands = load_model()
            label, confidence, annotated = predict_gesture(image, model, le, hands)
            
            if label:
                st.session_state.last_gesture = label
                st.session_state.detection_count += 1
                
                if st.session_state.voice_enabled:
                    threading.Thread(target=speak_gesture, args=(label,), daemon=True).start()
                
                st.image(annotated, caption="Detected Hand Landmarks", width=600)
    else:
        st.info("👆 Upload an image to detect hand gestures")
    
    st.markdown("""
    <div class='info-card'>
        <h4 style='color: #667eea;'>ℹ️ Instructions</h4>
        <ul style='text-align: left; color: #666;'>
            <li>Upload clear image of hand gesture</li>
            <li>Good lighting recommended</li>
            <li>Show full hand in frame</li>
            <li>37 gestures: A-Z, 0-9, Space</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.session_state.subtitles_enabled:
        st.markdown("<div class='info-card'><h3 style='color: #667eea; text-align: center;'>💬 Detected Gesture</h3></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='prediction-box'>
            <div class='prediction-text'>"{st.session_state.last_gesture}"</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div class='info-card'><h3 style='color: #667eea; text-align: center;'>🎯 Quick Stats</h3></div>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-number'>{'✅' if st.session_state.voice_enabled else '❌'}</div>
            <div class='stat-label'>Voice</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-number'>{'✅' if st.session_state.subtitles_enabled else '❌'}</div>
            <div class='stat-label'>Subtitles</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='info-card' style='text-align: center;'><p style='color: #667eea; font-weight: 600;'>Made with ❤️ | <a href='https://github.com/deveshrx/sign-language-detections' target='_blank' style='color: #f5576c;'>GitHub</a></p></div>", unsafe_allow_html=True)
