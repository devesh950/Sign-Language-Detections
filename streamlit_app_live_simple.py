import streamlit as st
import cv2
import numpy as np
import os
import time
os.environ['KERAS_BACKEND'] = 'jax'

from live_sign_detect import Detector
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Live Sign Language Detection",
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'detector' not in st.session_state:
    with st.spinner("🔄 Loading AI model... This may take a moment..."):
        st.session_state.detector = Detector()
        st.success("✅ Model loaded successfully!")

if 'current_detection' not in st.session_state:
    st.session_state.current_detection = {"label": "No detection yet", "confidence": 0.0}

if 'show_subtitles' not in st.session_state:
    st.session_state.show_subtitles = True

if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# Main header
st.markdown('<h1 class="main-header">🤟 Live Sign Language Detection</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Controls")
    
    # START/STOP button
    if st.button("🎬 START LIVE DETECTION" if not st.session_state.is_running else "⏹️ STOP DETECTION", 
                 type="primary", use_container_width=True):
        st.session_state.is_running = not st.session_state.is_running
        st.rerun()
    
    # Status indicator
    if st.session_state.is_running:
        st.success("🟢 **LIVE** - Continuously detecting...")
        st.info("💡 **Tip**: Keep clicking 'Take Photo' button repeatedly for continuous detection!")
    else:
        st.info("⚪ **STOPPED** - Click START to begin")
    
    st.markdown("---")
    
    # Subtitles toggle
    subtitle_label = "📝 Subtitles: ON" if st.session_state.show_subtitles else "📝 Subtitles: OFF"
    if st.button(subtitle_label, use_container_width=True):
        st.session_state.show_subtitles = not st.session_state.show_subtitles
        st.rerun()
    
    st.markdown("---")
    
    # Info
    st.markdown("### 📊 Statistics")
    st.metric("Supported Gestures", "37")
    st.metric("Confidence Threshold", "80%")
    
    st.markdown("---")
    
    st.markdown("### 💡 Tips for Best Results")
    st.info("""
    **For accurate detection:**
    - Good lighting (face the light)
    - Hand 30-60cm from camera
    - Show full hand clearly
    - Hold gesture steady
    - Use plain background
    - Keep clicking 'Take Photo' for continuous feed
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
    st.markdown("### 📹 Live Camera Feed")
    
    if st.session_state.is_running:
        st.success("✅ **LIVE MODE ACTIVE** - Keep clicking 'Take Photo' repeatedly for continuous detection!")
        
        # Use browser camera input
        camera_photo = st.camera_input("📸 Camera Active - Click 'Take Photo' repeatedly", key="live_camera")
        
        if camera_photo is not None:
            # Read the image
            bytes_data = camera_photo.getvalue()
            image = Image.open(camera_photo)
            
            # Convert to numpy array
            frame = np.array(image)
            
            # Convert RGB to BGR (OpenCV format)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Automatically detect
            with st.spinner("🤖 Analyzing gesture..."):
                label, confidence, annotated_frame = st.session_state.detector.predict(frame_bgr)
                
                # Update detection
                if confidence >= 0.80:
                    st.session_state.current_detection = {"label": label, "confidence": confidence}
                elif confidence >= 0.60:
                    st.session_state.current_detection = {"label": f"{label} (uncertain)", "confidence": confidence}
                else:
                    st.session_state.current_detection = {"label": "No clear sign", "confidence": confidence}
                
                # Convert BGR to RGB for display
                annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                
                # Show annotated image
                st.image(annotated_frame_rgb, caption="🔍 Detected Frame with Hand Landmarks", use_container_width=True)
        else:
            st.info("📸 Waiting for first photo... Click the 'Take Photo' button above!")
            st.markdown("**💡 PRO TIP**: Click 'Take Photo' repeatedly for near-live detection!")
    else:
        st.warning("⏹️ **Camera Stopped**")
        st.info("👉 Click **START LIVE DETECTION** in the sidebar to begin!")
        st.markdown("""
        ### How Live Detection Works:
        1. Click **START** button in sidebar
        2. Allow camera access when prompted
        3. Keep clicking **'Take Photo'** button repeatedly
        4. Each click = instant analysis
        5. Results appear in real-time on the right →
        
        **This gives you continuous detection by rapidly taking photos!**
        """)

with col2:
    st.markdown("### 🎯 Live Detection Results")
    
    # Detection display
    if st.session_state.show_subtitles:
        detection = st.session_state.current_detection
        
        # Color based on confidence
        if detection['confidence'] >= 0.80:
            box_color = "background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);"
            confidence_emoji = "✅"
        elif detection['confidence'] >= 0.60:
            box_color = "background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"
            confidence_emoji = "⚠️"
        else:
            box_color = "background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"
            confidence_emoji = "❌"
        
        st.markdown(f"""
        <div style="{box_color} padding: 2rem; border-radius: 15px; text-align: center; color: white; margin: 1rem 0;">
            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                {detection['label']}
            </div>
            <div style="font-size: 1.5rem; opacity: 0.9;">
                {confidence_emoji} {detection['confidence']*100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicators
        st.markdown("### 📊 Confidence Status")
        
        # Confidence level
        conf_val = detection['confidence'] * 100
        if conf_val >= 80:
            st.success(f"✅ High Confidence ({conf_val:.1f}%)")
            st.markdown("**Result**: Very likely correct!")
        elif conf_val >= 60:
            st.warning(f"⚠️ Medium Confidence ({conf_val:.1f}%)")
            st.markdown("**Result**: Possibly correct")
        else:
            st.error(f"❌ Low Confidence ({conf_val:.1f}%)")
            st.markdown("**Result**: Unclear gesture")
        
        # Progress bar
        st.progress(detection['confidence'])
        
        # Tips based on result
        if conf_val < 80:
            st.markdown("---")
            st.markdown("### 💡 Improve Results")
            st.info("""
            **Try these:**
            - Better lighting
            - Show full hand
            - Plain background
            - Hold steady
            - Check supported gestures
            """)
    else:
        st.info("📝 Subtitles disabled. Enable in sidebar.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🤟 Live Sign Language Detection | Built with Streamlit & MediaPipe</p>
    <p>💡 Keep clicking 'Take Photo' for continuous detection!</p>
</div>
""", unsafe_allow_html=True)
