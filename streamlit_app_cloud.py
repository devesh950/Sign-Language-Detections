import streamlit as st
import cv2
import numpy as np
import os

# CRITICAL: Set Keras backend BEFORE importing keras
os.environ['KERAS_BACKEND'] = 'jax'

from live_sign_detect import Detector
from PIL import Image
import threading
import time

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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detector' not in st.session_state:
    with st.spinner('🔄 Loading AI model...'):
        try:
            st.session_state.detector = Detector(
                model_path='sign_model.h5',
                labels_path='labels.pkl',
                buffer_len=5,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            st.success('✅ Model loaded successfully!')
        except Exception as e:
            st.error(f"❌ Failed to load model: {str(e)}")
            st.stop()

if 'show_subtitles' not in st.session_state:
    st.session_state.show_subtitles = True
if 'current_detection' not in st.session_state:
    st.session_state.current_detection = {"label": "No hand detected", "confidence": 0.0}
if 'run_detection' not in st.session_state:
    st.session_state.run_detection = False

# Main header
st.markdown('<h1 class="main-header">🤟 Sign Language Detection</h1>', unsafe_allow_html=True)

# Info banner
st.info("📷 **Note:** This app requires camera access. Please allow camera permissions when prompted by your browser.")

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Controls")
    
    # Camera control
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📷 Start Detection", use_container_width=True):
            st.session_state.run_detection = True
            st.rerun()
    with col2:
        if st.button("⏹️ Stop Detection", use_container_width=True):
            st.session_state.run_detection = False
            st.rerun()
    
    st.markdown("---")
    
    # Subtitles toggle
    st.session_state.show_subtitles = st.checkbox("📝 Show Subtitles", value=st.session_state.show_subtitles)
    
    st.markdown("---")
    
    # Info
    st.markdown("### 📊 Statistics")
    st.metric("Supported Gestures", "37")
    st.metric("Confidence Threshold", "80%")
    st.metric("Detection Status", "Running" if st.session_state.run_detection else "Stopped")
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips for Accuracy")
    st.info("""
    **For best results:**
    - ☀️ Good lighting (face light source)
    - 📏 Keep hand 30-60cm from camera
    - ✋ Show full hand clearly
    - ⏸️ Hold gesture steady 1-2 seconds
    - 🏞️ Use plain background
    - 🎯 Make clear, distinct gestures
    """)
    
    st.markdown("---")
    
    st.markdown("### 🤝 Supported Gestures")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Letters:**
        - A through Z
        - (26 gestures)
        """)
    with col_b:
        st.markdown("""
        **Numbers:**
        - 0 through 9
        - + Space
        - (11 gestures)
        """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📹 Camera Feed")
    
    # Camera capture using Streamlit's camera_input
    camera_image = st.camera_input("Show your hand sign", disabled=not st.session_state.run_detection)
    
    if camera_image is not None and st.session_state.run_detection:
        # Convert uploaded image to OpenCV format
        file_bytes = np.asarray(bytearray(camera_image.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Detect sign language
        try:
            label, confidence, annotated_frame = st.session_state.detector.predict(frame)
            
            # Update detection
            if confidence >= 0.80:
                st.session_state.current_detection = {"label": label, "confidence": confidence}
            elif confidence >= 0.60:
                st.session_state.current_detection = {"label": f"{label} (uncertain)", "confidence": confidence}
            else:
                st.session_state.current_detection = {"label": "No clear sign detected", "confidence": confidence}
            
            # Display annotated frame
            annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            st.image(annotated_frame_rgb, channels="RGB", use_container_width=True)
            
        except Exception as e:
            st.error(f"Detection error: {str(e)}")
    else:
        if not st.session_state.run_detection:
            st.info("📷 Click 'Start Detection' to begin")
        else:
            st.warning("📸 Waiting for camera input...")

with col2:
    st.markdown("### 🎯 Detection Results")
    
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
            <div style="font-size: 2.5rem; font-weight: bold; margin-bottom: 0.5rem;">
                {detection['label']}
            </div>
            <div style="font-size: 1.3rem; opacity: 0.9;">
                Confidence: {detection['confidence']*100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicators
        st.markdown("### 📊 Status")
        
        # Detection status
        detection_status = "🟢 Detection Active" if st.session_state.run_detection else "🔴 Detection Stopped"
        detection_color = "green" if st.session_state.run_detection else "red"
        st.markdown(f":{detection_color}[{detection_status}]")
        
        # Confidence level
        conf_val = detection['confidence'] * 100
        if conf_val >= 80:
            st.markdown(f":green[✅ High Confidence ({conf_val:.1f}%)]")
        elif conf_val >= 60:
            st.markdown(f":orange[⚠️ Medium Confidence ({conf_val:.1f}%)]")
        else:
            st.markdown(f":red[❌ Low Confidence ({conf_val:.1f}%)]")
            
        # Recent detection history
        st.markdown("### 📜 Last Detection")
        st.code(f"{detection['label']} ({conf_val:.1f}%)")
    else:
        st.info("📝 Subtitles are disabled. Enable them in the sidebar.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🤟 Sign Language Detection System | Built with Streamlit, MediaPipe & Keras</p>
    <p>💡 Tip: Use good lighting and clear hand gestures for best results!</p>
    <p>⭐ Star on <a href="https://github.com/devesh950/Sign-Language-Detections" target="_blank">GitHub</a></p>
</div>
""", unsafe_allow_html=True)

# Instructions
with st.expander("ℹ️ How to Use This App"):
    st.markdown("""
    ### Getting Started
    
    1. **Click "Start Detection"** in the sidebar
    2. **Allow camera access** when prompted by your browser
    3. **Show your hand** to the camera
    4. **Make a gesture** (A-Z, 0-9, or Space)
    5. **Hold steady** for 1-2 seconds
    6. **See the result** in the Detection Results panel
    
    ### Tips for Best Accuracy
    
    - 💡 **Lighting**: Face a light source, avoid backlighting
    - 📏 **Distance**: Keep your hand 30-60cm (1-2 feet) from camera
    - ✋ **Position**: Show your full hand with all fingers visible
    - ⏸️ **Steadiness**: Hold the gesture steady for 1-2 seconds
    - 🎯 **Clarity**: Make clear, distinct gestures
    - 🏞️ **Background**: Use a plain, contrasting background
    
    ### Understanding Confidence Levels
    
    - **80-100%**: Accurate detection (displayed in green)
    - **60-79%**: Uncertain detection (displayed in orange, marked as "uncertain")
    - **0-59%**: Too low to display (shows "No clear sign detected")
    
    ### Troubleshooting
    
    - **Camera not working?** Check browser permissions
    - **Low accuracy?** Improve lighting and hand positioning
    - **No detection?** Ensure your full hand is visible
    - **App slow?** Close other browser tabs
    """)

# Technical info
with st.expander("🔧 Technical Details"):
    st.markdown("""
    ### Technology Stack
    
    - **Framework**: Streamlit (Python web framework)
    - **Hand Detection**: MediaPipe Hands
    - **AI Model**: Keras with JAX backend
    - **Computer Vision**: OpenCV
    - **Model Type**: Neural Network (37 gesture classes)
    
    ### Model Information
    
    - **Gestures**: 37 (A-Z letters, 0-9 numbers, Space)
    - **Input**: Hand landmarks (21 points per hand)
    - **Architecture**: Deep Neural Network
    - **Backend**: JAX (for fast inference)
    - **Confidence Threshold**: 80%
    - **Detection Confidence**: 70%
    - **Tracking Confidence**: 70%
    - **Buffer Size**: 5 frames
    
    ### Performance
    
    - **Latency**: Real-time (<100ms per frame)
    - **Accuracy**: 80%+ for clear gestures
    - **Frame Rate**: Depends on device camera
    """)
