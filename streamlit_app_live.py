import streamlit as st
import cv2
import numpy as np
import os
os.environ['KERAS_BACKEND'] = 'jax'

from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import av
from live_sign_detect import Detector
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

# Video transformer class
class SignLanguageTransformer(VideoTransformerBase):
    def __init__(self):
        self.detector = st.session_state.detector
        self.frame_count = 0
        
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Process every 2nd frame for performance
        self.frame_count += 1
        if self.frame_count % 2 == 0:
            # Detect sign language
            label, confidence, annotated_frame = self.detector.predict(img)
            
            # Update session state
            if confidence >= 0.80:
                st.session_state.current_detection = {"label": label, "confidence": confidence}
            elif confidence >= 0.60:
                st.session_state.current_detection = {"label": f"{label} (uncertain)", "confidence": confidence}
            else:
                st.session_state.current_detection = {"label": "No clear sign detected", "confidence": confidence}
            
            return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")
        else:
            return av.VideoFrame.from_ndarray(img, format="bgr24")

# Main header
st.markdown('<h1 class="main-header">🤟 Sign Language Detection - Live</h1>', unsafe_allow_html=True)

st.info("📹 **Click 'START' to begin live detection** | Click 'STOP' to pause | Show hand gestures to camera")

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ Controls")
    
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
    st.markdown("### 📹 Live Camera Feed")
    
    # WebRTC video streamer
    webrtc_ctx = webrtc_streamer(
        key="sign-language-detection",
        mode=WebRtcMode.SENDRECV,
        video_transformer_factory=SignLanguageTransformer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.markdown("### 🎯 Detection Results")
    
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
                {confidence_emoji} Confidence: {detection['confidence']*100:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicators
        st.markdown("### 📊 Status")
        
        # Camera status
        if webrtc_ctx.state.playing:
            st.success("📹 Camera Active")
        else:
            st.info("⏹️ Camera Stopped")
        
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
            st.markdown("**Result**: Unclear")
    else:
        st.info("📝 Subtitles are disabled. Enable them in the sidebar.")
    
    # Detection info
    st.markdown("---")
    st.markdown("### 📜 Detection Info")
    
    if st.session_state.current_detection['label'] != "No detection yet":
        st.markdown(f"**Last Detected**: {st.session_state.current_detection['label']}")
        st.progress(st.session_state.current_detection['confidence'])
    else:
        st.markdown("*Click START to begin detecting*")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🤟 Sign Language Detection System | Built with Streamlit & MediaPipe</p>
    <p>💡 Tip: Use good lighting and clear hand gestures for best results!</p>
    <p>📱 Works on desktop browsers with camera access!</p>
</div>
""", unsafe_allow_html=True)
