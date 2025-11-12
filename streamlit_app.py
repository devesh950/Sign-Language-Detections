import streamlit as st
import cv2
import numpy as np
import os
os.environ['KERAS_BACKEND'] = 'jax'

from live_sign_detect import Detector
import pyttsx3
import threading
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Sign Language Detection",
    page_icon="🤟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .detection-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    .detection-label {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .detection-confidence {
        font-size: 1.5rem;
        opacity: 0.9;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detector' not in st.session_state:
    with st.spinner('🔄 Loading AI model...'):
        st.session_state.detector = Detector(
            model_path='sign_model.h5',
            labels_path='labels.pkl',
            buffer_len=5,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    st.success('✅ Model loaded successfully!')

if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True
if 'show_subtitles' not in st.session_state:
    st.session_state.show_subtitles = True
if 'last_spoken' not in st.session_state:
    st.session_state.last_spoken = ""
if 'current_detection' not in st.session_state:
    st.session_state.current_detection = {"label": "No hand detected", "confidence": 0.0}

# Voice synthesis function (runs in background)
def speak_async(text):
    def speak_thread():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except:
            pass
    
    thread = threading.Thread(target=speak_thread, daemon=True)
    thread.start()

# Main header
st.markdown('<h1 class="main-header">🤟 Sign Language Detection</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Controls")
    
    # Camera control
    if st.button("📷 Start Camera" if not st.session_state.camera_active else "⏹️ Stop Camera"):
        st.session_state.camera_active = not st.session_state.camera_active
        if not st.session_state.camera_active:
            st.session_state.current_detection = {"label": "Camera stopped", "confidence": 0.0}
    
    st.markdown("---")
    
    # Voice toggle
    voice_label = "🔊 Voice: ON" if st.session_state.voice_enabled else "🔇 Voice: OFF"
    if st.button(voice_label):
        st.session_state.voice_enabled = not st.session_state.voice_enabled
        st.rerun()
    
    # Subtitles toggle
    subtitle_label = "📝 Subtitles: ON" if st.session_state.show_subtitles else "📝 Subtitles: OFF"
    if st.button(subtitle_label):
        st.session_state.show_subtitles = not st.session_state.show_subtitles
        st.rerun()
    
    st.markdown("---")
    
    # Info
    st.markdown("### 📊 Statistics")
    st.metric("Supported Gestures", "37")
    st.metric("Confidence Threshold", "80%")
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips")
    st.info("""
    **For best accuracy:**
    - Good lighting (face light source)
    - Keep hand 30-60cm from camera
    - Show full hand clearly
    - Hold gesture steady 1-2 seconds
    - Use plain background
    """)
    
    st.markdown("---")
    
    st.markdown("### 🤝 Supported Gestures")
    st.markdown("""
    - **Letters**: A-Z (26)
    - **Numbers**: 0-9 (10)
    - **Special**: Space (1)
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📹 Camera Feed")
    camera_placeholder = st.empty()
    
    if st.session_state.camera_active:
        # Open camera
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_count = 0
        
        # Process frames
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            
            # Process every 2nd frame
            if frame_count % 2 == 0:
                # Detect sign language
                label, confidence, annotated_frame = st.session_state.detector.predict(frame)
                
                # Update detection
                if confidence >= 0.80:
                    st.session_state.current_detection = {"label": label, "confidence": confidence}
                    
                    # Voice output
                    if st.session_state.voice_enabled and label != st.session_state.last_spoken:
                        speak_async(label)
                        st.session_state.last_spoken = label
                        
                elif confidence >= 0.60:
                    st.session_state.current_detection = {"label": f"{label} (uncertain)", "confidence": confidence}
                else:
                    st.session_state.current_detection = {"label": "No clear sign detected", "confidence": confidence}
                
                # Convert BGR to RGB for display
                annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                
                # Display frame
                camera_placeholder.image(annotated_frame_rgb, channels="RGB", use_container_width=True)
            else:
                # Just show the frame without processing
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                camera_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
        
        cap.release()
    else:
        # Show placeholder when camera is off
        camera_placeholder.info("📷 Click 'Start Camera' in the sidebar to begin detection")

with col2:
    st.markdown("### 🎯 Detection Results")
    
    # Detection display
    if st.session_state.show_subtitles:
        detection = st.session_state.current_detection
        
        # Color based on confidence
        if detection['confidence'] >= 0.80:
            box_color = "background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);"
        elif detection['confidence'] >= 0.60:
            box_color = "background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"
        else:
            box_color = "background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"
        
        st.markdown(f"""
        <div style="{box_color} padding: 2rem; border-radius: 15px; text-align: center; color: white; margin: 1rem 0;">
            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                {detection['label']}
            </div>
            <div style="font-size: 1.5rem; opacity: 0.9;">
                Confidence: {detection['confidence']*100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicators
        st.markdown("### 📊 Status")
        
        # Voice status
        voice_status = "🔊 Voice Active" if st.session_state.voice_enabled else "🔇 Voice Muted"
        voice_color = "green" if st.session_state.voice_enabled else "gray"
        st.markdown(f":{voice_color}[{voice_status}]")
        
        # Camera status
        camera_status = "📹 Camera Running" if st.session_state.camera_active else "⏹️ Camera Stopped"
        camera_color = "green" if st.session_state.camera_active else "gray"
        st.markdown(f":{camera_color}[{camera_status}]")
        
        # Confidence level
        conf_val = detection['confidence'] * 100
        if conf_val >= 80:
            st.markdown(f":green[✅ High Confidence ({conf_val:.1f}%)]")
        elif conf_val >= 60:
            st.markdown(f":orange[⚠️ Medium Confidence ({conf_val:.1f}%)]")
        else:
            st.markdown(f":red[❌ Low Confidence ({conf_val:.1f}%)]")
    else:
        st.info("📝 Subtitles are disabled. Enable them in the sidebar.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🤟 Sign Language Detection System | Built with Streamlit & MediaPipe</p>
    <p>💡 Tip: Use good lighting and clear hand gestures for best results!</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh if camera is active
if st.session_state.camera_active:
    import time
    time.sleep(0.1)
    st.rerun()
