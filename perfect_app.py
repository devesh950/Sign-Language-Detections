"""
Perfect Sign Language Detection App
Beautiful UI with Start/Stop Camera, Voice, and Subtitles controls
"""

import os
os.environ['KERAS_BACKEND'] = 'jax'

from flask import Flask, render_template_string, Response, jsonify, request
import cv2
import threading
import time
from live_sign_detect import Detector

app = Flask(__name__)

# Global variables
detector = None
camera = None
current_detection = {"label": "Ready to start", "confidence": 0.0}
camera_lock = threading.Lock()
is_camera_running = False
show_subtitles = True
voice_enabled = True
last_spoken = ""

# Load model on startup
print("🔄 Loading AI model...")
detector = Detector()
print("✅ Model loaded!\n")

# HTML Template with Beautiful UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🤟 Sign Language Detection</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeInDown 0.6s ease;
        }
        
        .header h1 {
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 3fr 1fr;
            gap: 25px;
            margin-top: 30px;
        }
        
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: fadeInUp 0.8s ease;
        }
        
        .video-section {
            position: relative;
        }
        
        .video-container {
            position: relative;
            width: 100%;
            border-radius: 12px;
            overflow: hidden;
            background: #1a1a1a;
            min-height: 480px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .video-placeholder {
            color: #888;
            font-size: 1.5em;
            text-align: center;
            padding: 40px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            flex: 1;
            min-width: 140px;
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
        }
        
        .btn-toggle {
            background: #e9ecef;
            color: #495057;
        }
        
        .btn-toggle.active {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .btn-toggle:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .detection-panel h2 {
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .detection-display {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
            min-height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            animation: pulse 2s infinite;
        }
        
        .detection-label {
            font-size: 3.5em;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.3);
            word-break: break-word;
        }
        
        .detection-confidence {
            font-size: 1.4em;
            opacity: 0.9;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: blink 2s infinite;
        }
        
        .status-active {
            background: #4caf50;
        }
        
        .status-inactive {
            background: #f44336;
        }
        
        .info-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 20px;
        }
        
        .info-box h3 {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #667eea;
        }
        
        .info-box ul {
            list-style: none;
            padding-left: 0;
        }
        
        .info-box li {
            padding: 8px 0;
            color: #555;
            display: flex;
            align-items: center;
        }
        
        .info-box li:before {
            content: "✓";
            color: #4caf50;
            font-weight: bold;
            margin-right: 10px;
        }
        
        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
            50% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
            .detection-label { font-size: 2.5em; }
            .controls { flex-direction: column; }
            .btn { min-width: 100%; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤟 Sign Language Detection</h1>
            <p>AI-Powered Real-Time Gesture Recognition</p>
        </div>

        <div class="main-content">
            <!-- Video Section -->
            <div class="card video-section">
                <h2 style="margin-bottom: 15px; color: #333;">
                    <span id="cameraStatus" class="status-indicator status-inactive"></span>
                    Camera Feed
                </h2>
                <div class="video-container" id="videoContainer">
                    <div class="video-placeholder" id="videoPlaceholder">
                        📷 Click "Start Camera" to begin
                    </div>
                    <img id="videoFeed" style="display: none;" alt="Camera Feed">
                </div>

                <div class="controls">
                    <button class="btn btn-primary" id="startBtn" onclick="startCamera()">
                        ▶️ Start Camera
                    </button>
                    <button class="btn btn-danger" id="stopBtn" onclick="stopCamera()" disabled>
                        ⏹️ Stop Camera
                    </button>
                    <button class="btn btn-toggle" id="voiceBtn" onclick="toggleVoice()">
                        🔊 Voice ON
                    </button>
                    <button class="btn btn-toggle" id="subtitlesBtn" onclick="toggleSubtitles()">
                        💬 Subtitles ON
                    </button>
                </div>
            </div>

            <!-- Detection Panel -->
            <div class="card detection-panel">
                <h2>Current Detection</h2>
                <div class="detection-display" id="detection">
                    <div class="detection-label" id="label">Ready</div>
                    <div class="detection-confidence" id="confidence">Start camera to detect</div>
                </div>

                <div class="info-box">
                    <h3>📋 Supported Gestures</h3>
                    <ul>
                        <li>Letters: A-Z (26 signs)</li>
                        <li>Numbers: 0-9 (10 signs)</li>
                        <li>Space gesture</li>
                        <li>Total: 37 gestures</li>
                    </ul>
                </div>

                <div class="info-box">
                    <h3>ℹ️ Instructions</h3>
                    <ul>
                        <li>Start the camera</li>
                        <li>Show hand to camera</li>
                        <li>Make a sign gesture</li>
                        <li>See result instantly!</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        let cameraRunning = false;
        let voiceEnabled = true;
        let subtitlesEnabled = true;

        function startCamera() {
            fetch('/start_camera', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        cameraRunning = true;
                        document.getElementById('videoFeed').src = '/video_feed?t=' + Date.now();
                        document.getElementById('videoFeed').style.display = 'block';
                        document.getElementById('videoPlaceholder').style.display = 'none';
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('stopBtn').disabled = false;
                        document.getElementById('cameraStatus').className = 'status-indicator status-active';
                        startDetectionUpdates();
                    }
                });
        }

        function stopCamera() {
            fetch('/stop_camera', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        cameraRunning = false;
                        document.getElementById('videoFeed').style.display = 'none';
                        document.getElementById('videoPlaceholder').style.display = 'block';
                        document.getElementById('videoPlaceholder').textContent = '📷 Camera stopped. Click "Start Camera" to resume';
                        document.getElementById('startBtn').disabled = false;
                        document.getElementById('stopBtn').disabled = true;
                        document.getElementById('cameraStatus').className = 'status-indicator status-inactive';
                        document.getElementById('label').textContent = 'Camera Off';
                        document.getElementById('confidence').textContent = 'Start camera to detect';
                    }
                });
        }

        function toggleVoice() {
            fetch('/toggle_voice', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    voiceEnabled = data.enabled;
                    const btn = document.getElementById('voiceBtn');
                    if (voiceEnabled) {
                        btn.classList.add('active');
                        btn.innerHTML = '🔊 Voice ON';
                    } else {
                        btn.classList.remove('active');
                        btn.innerHTML = '🔇 Voice OFF';
                    }
                });
        }

        function toggleSubtitles() {
            fetch('/toggle_subtitles', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    subtitlesEnabled = data.enabled;
                    const btn = document.getElementById('subtitlesBtn');
                    if (subtitlesEnabled) {
                        btn.classList.add('active');
                        btn.innerHTML = '💬 Subtitles ON';
                    } else {
                        btn.classList.remove('active');
                        btn.innerHTML = '💬 Subtitles OFF';
                    }
                });
        }

        function startDetectionUpdates() {
            setInterval(() => {
                if (cameraRunning) {
                    fetch('/get_detection')
                        .then(response => response.json())
                        .then(data => {
                            if (subtitlesEnabled) {
                                document.getElementById('label').textContent = data.label;
                                const conf = (data.confidence * 100).toFixed(1);
                                document.getElementById('confidence').textContent = 
                                    data.confidence > 0 ? `Confidence: ${conf}%` : 'Show your hand';
                            }
                        })
                        .catch(err => console.log('Detection update skipped'));
                }
            }, 500);
        }

        // Initialize button states
        window.onload = function() {
            document.getElementById('voiceBtn').classList.add('active');
            document.getElementById('subtitlesBtn').classList.add('active');
        };
    </script>
</body>
</html>
"""

def generate_frames():
    """Generate camera frames with detection"""
    global current_detection, is_camera_running
    
    frame_count = 0
    
    while is_camera_running:
        try:
            with camera_lock:
                if camera is None:
                    break
                success, frame = camera.read()
            
            if not success:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            
            # Process every 2nd frame for better accuracy
            if frame_count % 2 == 0:
                try:
                    label, confidence, annotated_frame = detector.predict(frame)
                    
                    # Higher confidence threshold (80%) for accurate results
                    if label and confidence >= 0.80:
                        current_detection = {
                            "label": label, 
                            "confidence": float(confidence)
                        }
                        frame = annotated_frame
                        
                        # Speak if voice enabled and different from last
                        if voice_enabled and label != globals().get('last_spoken', ''):
                            globals()['last_spoken'] = label
                            threading.Thread(target=speak_text, args=(label,), daemon=True).start()
                    elif label and confidence >= 0.60:
                        # Show low confidence detections but don't speak
                        current_detection = {
                            "label": f"{label} (uncertain)", 
                            "confidence": float(confidence)
                        }
                        frame = annotated_frame
                    else:
                        current_detection = {
                            "label": "No clear sign detected", 
                            "confidence": 0.0
                        }
                except Exception as e:
                    print(f"Detection error: {e}")
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        
        except Exception as e:
            print(f"Frame error: {e}")
            time.sleep(0.1)

def speak_text(text):
    """Speak text using TTS"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"Voice error: {e}")

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/start_camera', methods=['POST'])
def start_camera():
    """Start camera"""
    global camera, is_camera_running
    
    try:
        with camera_lock:
            if camera is None:
                camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                camera.set(cv2.CAP_PROP_FPS, 30)
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                # Warm up
                for _ in range(5):
                    camera.read()
        
        is_camera_running = True
        print("✅ Camera started")
        return jsonify({"success": True})
    except Exception as e:
        print(f"Camera start error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera"""
    global camera, is_camera_running
    
    try:
        is_camera_running = False
        time.sleep(0.5)  # Wait for frame generation to stop
        
        with camera_lock:
            if camera:
                camera.release()
                camera = None
        
        print("✅ Camera stopped")
        return jsonify({"success": True})
    except Exception as e:
        print(f"Camera stop error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/toggle_voice', methods=['POST'])
def toggle_voice():
    """Toggle voice output"""
    global voice_enabled
    voice_enabled = not voice_enabled
    print(f"🔊 Voice: {'ON' if voice_enabled else 'OFF'}")
    return jsonify({"enabled": voice_enabled})

@app.route('/toggle_subtitles', methods=['POST'])
def toggle_subtitles():
    """Toggle subtitles"""
    global show_subtitles
    show_subtitles = not show_subtitles
    print(f"💬 Subtitles: {'ON' if show_subtitles else 'OFF'}")
    return jsonify({"enabled": show_subtitles})

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_detection')
def get_detection():
    """Get current detection"""
    return jsonify(current_detection)

if __name__ == '__main__':
    # Get port from environment variable (for Render deployment) or use 5000 for local
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*70)
    print("🎉 PERFECT SIGN LANGUAGE DETECTION APP")
    print("="*70)
    print("\n✨ Features:")
    print("   • Beautiful Streamlit-style UI")
    print("   • Start/Stop Camera buttons")
    print("   • Voice ON/OFF toggle")
    print("   • Subtitles ON/OFF toggle")
    print("   • Real-time detection")
    print("   • Network access from phone/tablet")
    print("\n📱 ACCESS FROM:")
    print(f"   • Server running on port: {port}")
    if port == 5000:
        print("   • This computer:  http://localhost:5000")
        print("   • Phone/Tablet:   http://YOUR_LOCAL_IP:5000")
    print("\n💡 Open the URL in your browser and click 'Start Camera'!")
    print("\nPress Ctrl+C to stop")
    print("="*70 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)
    finally:
        is_camera_running = False
        if camera:
            camera.release()
        print("\n✅ Server stopped cleanly.")
