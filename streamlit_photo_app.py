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
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0;}
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    h1 {color: white; text-align: center; font-size: 56px; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 10px; animation: fadeIn 1s;}
    h2 {color: rgba(255,255,255,0.9); text-align: center; font-size: 24px; font-weight: 400; margin-bottom: 30px;}
    .stButton>button {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; font-size: 20px; font-weight: 600; padding: 15px 40px; border-radius: 50px; border: none; box-shadow: 0 8px 20px rgba(245,87,108,0.4); transition: all 0.3s ease; width: 100%; margin: 10px 0;}
    .stButton>button:hover {transform: translateY(-3px); box-shadow: 0 12px 30px rgba(245,87,108,0.6);}
    .prediction-box {background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 52%, #2BFF88 90%); padding: 40px; border-radius: 25px; text-align: center; color: white; box-shadow: 0 15px 40px rgba(0,0,0,0.3); margin: 20px 0; animation: pulse 2s infinite;}
    .prediction-text {font-size: 72px; font-weight: 700; margin: 10px 0; text-shadow: 3px 3px 6px rgba(0,0,0,0.4);}
    .confidence-text {font-size: 28px; font-weight: 600; opacity: 0.95;}
    .info-card {background: rgba(255,255,255,0.95); padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin: 15px 0; backdrop-filter: blur(10px);}
    .stat-box {background: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); flex: 1; margin: 0 10px;}
    .stat-number {font-size: 36px; font-weight: 700; color: #667eea;}
    .stat-label {font-size: 14px; color: #666; margin-top: 5px;}
    @keyframes fadeIn {from {opacity: 0; transform: translateY(-20px);} to {opacity: 1; transform: translateY(0);}}
    @keyframes pulse {0%, 100% {transform: scale(1);} 50% {transform: scale(1.02);}}
</style>
""", unsafe_allow_html=True)

if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True
if 'subtitles_enabled' not in st.session_state:
    st.session_state.subtitles_enabled = True
if 'detection_count' not in st.session_state:
    st.session_state.detection_count = 0
if 'last_gesture' not in st.session_state:
    st.session_state.last_gesture = "None"
if 'show_camera' not in st.session_state:
    st.session_state.show_camera = False
if 'voice_available' not in st.session_state:
    # Check if voice is available
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.stop()
        st.session_state.voice_available = True
    except:
        st.session_state.voice_available = False

@st.cache_resource
def load_model():
    model = keras.models.load_model('sign_model.h5')
    with open('labels.pkl', 'rb') as f:
        le = pickle.load(f)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True, 
        max_num_hands=1, 
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    return model, le, hands

def speak_gesture(text):
    """Speak gesture using text-to-speech (only works locally, not on Streamlit Cloud)"""
    if not st.session_state.voice_available:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        # Silently fail if voice not available
        st.session_state.voice_available = False

def normalize_landmarks(hand_landmarks):
    """Normalize landmarks by translating to wrist and scaling"""
    pts = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark], dtype=np.float32)
    wrist = pts[0]
    pts -= wrist
    scale = np.max(np.linalg.norm(pts, axis=1))
    if scale > 0:
        pts /= scale
    return pts.flatten()

def predict_gesture(image_pil, model, le, hands):
    img_array = np.array(image_pil)
    if len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)
    if img_array.shape[2] == 4:
        img_array = img_array[:, :, :3]
    
    h, w = img_array.shape[:2]
    res = hands.process(img_array)
    
    if res.multi_hand_landmarks:
        hand_landmarks = res.multi_hand_landmarks[0]
        
        # Normalize landmarks like in live_sign_detect.py
        landmarks = normalize_landmarks(hand_landmarks)
        landmarks = landmarks.reshape(1, -1)
        
        prediction = model.predict(landmarks, verbose=0)
        
        top_3_indices = np.argsort(prediction[0])[-3:][::-1]
        top_3_labels = le.inverse_transform(top_3_indices)
        top_3_confidences = prediction[0][top_3_indices]
        
        predicted_class = np.argmax(prediction, axis=1)
        confidence = float(np.max(prediction))
        
        if confidence > 0.50:
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
            
            return label, confidence, Image.fromarray(annotated), list(zip(top_3_labels, top_3_confidences))
    
    return None, None, image_pil, None

st.markdown("<h1>🤟 Sign Language Detection System</h1>", unsafe_allow_html=True)
st.markdown("<h2>Capture Photo or Upload Image for Hand Gesture Recognition</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("#### 🎤 Voice Output")
    st.session_state.voice_enabled = st.toggle("Enable Voice", value=st.session_state.voice_enabled)
    if not st.session_state.voice_available:
        st.warning("🔇 Voice unavailable on cloud. Works when running locally!")
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
    st.markdown("<div class='info-card'><h3 style='color: #667eea; text-align: center;'>📸 Capture or Upload Photo</h3></div>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📷 Take Photo", "📁 Upload File"])
    
    with tab1:
        st.markdown("<div style='text-align: center; margin: 20px 0;'><button style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; font-size: 18px; font-weight: 600; padding: 12px 30px; border-radius: 25px; border: none; cursor: pointer;'>Click to Enable Camera 📷</button></div>", unsafe_allow_html=True)
        
        if st.button("🎥 Open Camera", key="open_camera", use_container_width=True):
            st.session_state.show_camera = True
        
        if st.session_state.show_camera:
            camera_photo = st.camera_input("Show your hand gesture to camera", label_visibility="collapsed", key="camera_input")
            if camera_photo:
                image = Image.open(camera_photo)
                st.markdown("<p style='text-align: center; color: #667eea; font-weight: 600; font-size: 18px;'>📸 Captured Photo</p>", unsafe_allow_html=True)
                
                with st.spinner('🔍 Detecting gesture...'):
                    model, le, hands = load_model()
                    label, confidence, annotated, top_3 = predict_gesture(image, model, le, hands)
                    
                    if label:
                        st.session_state.last_gesture = label
                        st.session_state.detection_count += 1
                        
                        if st.session_state.voice_enabled:
                            # Try system voice (local only)
                            threading.Thread(target=speak_gesture, args=(label,), daemon=True).start()
                            # Also use browser speech synthesis (works on cloud!)
                            st.markdown(f"""
                            <script>
                                if ('speechSynthesis' in window) {{
                                    var msg = new SpeechSynthesisUtterance('{label}');
                                    msg.rate = 1.0;
                                    window.speechSynthesis.speak(msg);
                                }}
                            </script>
                            """, unsafe_allow_html=True)
                        
                        st.image(annotated, use_container_width=True)
                        st.success(f"✅ Detected: **{label}** (Confidence: {confidence*100:.1f}%)")
                        
                        if confidence < 0.70:
                            st.warning(f"⚠️ Low confidence ({confidence*100:.1f}%). Try better lighting or clearer hand position.")
                        
                        if top_3:
                            st.markdown("**Top 3 Predictions:**")
                            for i, (pred_label, pred_conf) in enumerate(top_3, 1):
                                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                                st.write(f"{emoji} {i}. **{pred_label}** - {pred_conf*100:.1f}%")
                    else:
                        st.image(image, use_container_width=True)
                        st.warning("⚠️ No hand detected. Please show your hand clearly to camera.")
            
            if st.button("❌ Close Camera", key="close_camera"):
                st.session_state.show_camera = False
                st.rerun()
        else:
            st.info("👆 Click 'Open Camera' button to start capturing photos")
    
    with tab2:
        uploaded = st.file_uploader("Choose a hand gesture image...", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
        
        if uploaded:
            image = Image.open(uploaded)
            st.markdown("<p style='text-align: center; color: #667eea; font-weight: 600; font-size: 18px;'>📁 Uploaded Image</p>", unsafe_allow_html=True)
            
            with st.spinner('🔍 Detecting gesture...'):
                model, le, hands = load_model()
                label, confidence, annotated, top_3 = predict_gesture(image, model, le, hands)
                
                if label:
                    st.session_state.last_gesture = label
                    st.session_state.detection_count += 1
                    
                    if st.session_state.voice_enabled:
                        # Try system voice (local only)
                        threading.Thread(target=speak_gesture, args=(label,), daemon=True).start()
                        # Also use browser speech synthesis (works on cloud!)
                        st.markdown(f"""
                        <script>
                            if ('speechSynthesis' in window) {{
                                var msg = new SpeechSynthesisUtterance('{label}');
                                msg.rate = 1.0;
                                window.speechSynthesis.speak(msg);
                            }}
                        </script>
                        """, unsafe_allow_html=True)
                    
                    st.image(annotated, use_container_width=True)
                    st.success(f"✅ Detected: **{label}** (Confidence: {confidence*100:.1f}%)")
                    
                    if confidence < 0.70:
                        st.warning(f"⚠️ Low confidence. Check top 3 predictions below or try better lighting/clearer hand.")
                    
                    if top_3:
                        st.markdown("**Top 3 Predictions:**")
                        for i, (pred_label, pred_conf) in enumerate(top_3, 1):
                            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                            st.write(f"{emoji} {i}. **{pred_label}** - {pred_conf*100:.1f}%")
                else:
                    st.image(image, use_container_width=True)
                    st.warning("⚠️ No hand detected. Please upload image with visible hand.")
    
    st.markdown("""
    <div class='info-card'>
        <h4 style='color: #667eea;'>ℹ️ Instructions</h4>
        <ul style='text-align: left; color: #666;'>
            <li>Use 📷 <b>Take Photo</b> to capture from webcam</li>
            <li>Use 📁 <b>Upload File</b> to select saved image</li>
            <li><b>Show full hand clearly</b> - all fingers visible</li>
            <li><b>Good lighting</b> - avoid shadows on hand</li>
            <li><b>Plain background</b> - helps detection</li>
            <li><b>Hold gesture steady</b> - keep hand still</li>
            <li>37 gestures: A-Z, 0-9, Space</li>
        </ul>
        <p style='color: #f5576c; font-weight: 600;'>💡 Tip: If wrong gesture detected, check Top 3 predictions - correct one might be there!</p>
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
