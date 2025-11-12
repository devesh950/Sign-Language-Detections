"""
Perfect Sign Language Detection App - BROWSER CAMERA VERSION
Works on cloud servers (Render.com) by using browser's webcam via JavaScript
"""

import os
os.environ['KERAS_BACKEND'] = 'jax'

from flask import Flask, render_template_string, jsonify, request
import cv2
import numpy as np
import base64
from live_sign_detect import Detector

app = Flask(__name__)

# Global variables
detector = None
current_detection = {"label": "Ready to start", "confidence": 0.0}
show_subtitles = True
voice_enabled = True
last_spoken = ""

# Load model on startup
print("🔄 Loading AI model...")
detector = Detector()
print("✅ Model loaded!\n")

# HTML Template with Browser Camera Access
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
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            animation: fadeInDown 0.8s ease;
        }
        
        .header h1 {
            font-size: 3rem;
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
            background: #000;
            border-radius: 12px;
            overflow: hidden;
            aspect-ratio: 4/3;
        }
        
        #videoElement {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        #canvasElement {
            display: none;
        }
        
        .subtitle-overlay {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: #00ff00;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            min-width: 300px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(0, 255, 0, 0.3);
            display: none;
        }
        
        .subtitle-overlay.show {
            display: block;
            animation: pulse 1s infinite;
        }
        
        .confidence {
            font-size: 1rem;
            color: #88ff88;
            margin-top: 5px;
        }
        
        .controls-panel {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .control-section {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
        }
        
        .control-section h3 {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .toggle-btn {
            background: #e9ecef;
            color: #495057;
        }
        
        .toggle-btn.active {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: white;
            border-radius: 8px;
            font-size: 0.9rem;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #dc3545;
            animation: blink 2s infinite;
        }
        
        .status-dot.active {
            background: #28a745;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }
        
        .stat-item {
            background: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .info-box p {
            font-size: 0.9rem;
            color: #0d47a1;
            line-height: 1.6;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: translateX(-50%) scale(1);
            }
            50% {
                transform: translateX(-50%) scale(1.05);
            }
        }
        
        @keyframes blink {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.3;
            }
        }
        
        @media (max-width: 968px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤟 Sign Language Detection</h1>
            <p style="font-size: 1.2rem; opacity: 0.9;">Real-time ASL recognition with AI</p>
        </div>
        
        <div class="main-content">
            <!-- Video Section -->
            <div class="card video-section">
                <div class="video-container">
                    <video id="videoElement" autoplay playsinline></video>
                    <canvas id="canvasElement"></canvas>
                    <div id="subtitleOverlay" class="subtitle-overlay">
                        <div id="detectionText">Ready to start</div>
                        <div class="confidence" id="confidenceText">0%</div>
                    </div>
                </div>
                
                <div class="info-box">
                    <p>
                        <strong>📱 Browser Camera:</strong> This app uses your browser's webcam. 
                        Click "Start Camera" and allow camera access when prompted. 
                        Works on any device with a camera!
                    </p>
                </div>
            </div>
            
            <!-- Controls Section -->
            <div class="controls-panel">
                <!-- Camera Controls -->
                <div class="card control-section">
                    <h3>📷 Camera Controls</h3>
                    <button id="startBtn" class="btn btn-primary" onclick="startCamera()">
                        ▶️ Start Camera
                    </button>
                    <button id="stopBtn" class="btn btn-danger" onclick="stopCamera()" disabled>
                        ⏹️ Stop Camera
                    </button>
                    
                    <div class="status-indicator" style="margin-top: 15px;">
                        <div id="statusDot" class="status-dot"></div>
                        <span id="statusText">Camera Stopped</span>
                    </div>
                </div>
                
                <!-- Display Controls -->
                <div class="card control-section">
                    <h3>⚙️ Display Options</h3>
                    <button id="subtitlesBtn" class="btn toggle-btn active" onclick="toggleSubtitles()">
                        💬 Subtitles: ON
                    </button>
                    <button id="voiceBtn" class="btn toggle-btn active" onclick="toggleVoice()">
                        🔊 Voice: ON
                    </button>
                </div>
                
                <!-- Statistics -->
                <div class="card control-section">
                    <h3>📊 Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value" id="fpsCounter">0</div>
                            <div class="stat-label">FPS</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="detectionCounter">0</div>
                            <div class="stat-label">Detections</div>
                        </div>
                    </div>
                </div>
                
                <!-- Gesture Info -->
                <div class="card control-section">
                    <h3>✋ Supported Gestures</h3>
                    <div style="font-size: 0.9rem; line-height: 1.8;">
                        <p><strong>Letters:</strong> A-Z (26)</p>
                        <p><strong>Numbers:</strong> 0-9 (10)</p>
                        <p><strong>Special:</strong> Space (1)</p>
                        <p style="margin-top: 10px; color: #667eea;"><strong>Total: 37 gestures</strong></p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let videoElement = document.getElementById('videoElement');
        let canvasElement = document.getElementById('canvasElement');
        let ctx = canvasElement.getContext('2d');
        let stream = null;
        let isRunning = false;
        let detectionInterval = null;
        let showSubtitles = true;
        let voiceEnabled = true;
        let detectionCount = 0;
        let fpsCount = 0;
        let lastFpsUpdate = Date.now();

        // Start camera
        async function startCamera() {
            try {
                console.log('Requesting camera access...');
                
                // Check if getUserMedia is supported
                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    alert('❌ Camera not supported in this browser. Please use Chrome, Firefox, or Edge.');
                    return;
                }
                
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        width: { ideal: 640 },
                        height: { ideal: 480 },
                        facingMode: 'user'
                    } 
                });
                
                console.log('Camera access granted');
                videoElement.srcObject = stream;
                
                // Wait for video to load
                await new Promise((resolve) => {
                    videoElement.onloadedmetadata = () => {
                        videoElement.play();
                        resolve();
                    };
                });
                
                isRunning = true;
                
                // Set canvas size
                canvasElement.width = 640;
                canvasElement.height = 480;
                
                // Update UI
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('statusDot').classList.add('active');
                document.getElementById('statusText').textContent = 'Camera Running';
                
                console.log('Starting detection loop...');
                
                // Start detection loop
                startDetection();
                
            } catch (error) {
                console.error('Camera error:', error);
                let errorMsg = '❌ Camera Error: ';
                if (error.name === 'NotAllowedError') {
                    errorMsg += 'Camera access denied. Please allow camera permissions in your browser.';
                } else if (error.name === 'NotFoundError') {
                    errorMsg += 'No camera found on this device.';
                } else if (error.name === 'NotReadableError') {
                    errorMsg += 'Camera is already in use by another application.';
                } else {
                    errorMsg += error.message || 'Unknown error occurred.';
                }
                alert(errorMsg);
            }
        }

        // Stop camera
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
                stream = null;
            }
            
            isRunning = false;
            
            if (detectionInterval) {
                clearInterval(detectionInterval);
                detectionInterval = null;
            }
            
            // Update UI
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('statusDot').classList.remove('active');
            document.getElementById('statusText').textContent = 'Camera Stopped';
            document.getElementById('subtitleOverlay').classList.remove('show');
        }

        // Start detection loop - OPTIMIZED FOR SPEED
        function startDetection() {
            let frameCount = 0;
            let isProcessing = false;
            
            detectionInterval = setInterval(async () => {
                if (!isRunning || isProcessing) {
                    return; // Skip if already processing
                }
                
                frameCount++;
                
                // Process every 3rd frame (333ms) to reduce server load
                if (frameCount % 3 !== 0) {
                    return;
                }
                
                isProcessing = true;
                
                try {
                    // Draw video frame to canvas
                    ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
                    
                    // Convert canvas to base64 with lower quality for speed
                    const imageData = canvasElement.toDataURL('image/jpeg', 0.5);
                    
                    // Send to server with timeout
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 sec timeout
                    
                    const response = await fetch('/process_frame', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            image: imageData
                        }),
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        console.error(`Server error: ${response.status}`);
                        console.log('Detection update skipped');
                        return;
                    }
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        updateDetection(data);
                    } else {
                        console.error('Detection failed:', data.error);
                    }
                    
                } catch (error) {
                    if (error.name === 'AbortError') {
                        console.error('Request timeout');
                    } else {
                        console.error('Detection error:', error);
                    }
                } finally {
                    isProcessing = false;
                }
            }, 100); // Check every 100ms, but process every 300ms
        }

        // Update detection display
        function updateDetection(data) {
            const overlay = document.getElementById('subtitleOverlay');
            const detectionText = document.getElementById('detectionText');
            const confidenceText = document.getElementById('confidenceText');
            
            if (showSubtitles && data.label !== "No hand detected") {
                detectionText.textContent = data.label;
                confidenceText.textContent = Math.round(data.confidence * 100) + '%';
                overlay.classList.add('show');
                detectionCount++;
                document.getElementById('detectionCounter').textContent = detectionCount;
            } else {
                overlay.classList.remove('show');
            }
            
            // Update FPS
            fpsCount++;
            const now = Date.now();
            if (now - lastFpsUpdate >= 1000) {
                document.getElementById('fpsCounter').textContent = fpsCount;
                fpsCount = 0;
                lastFpsUpdate = now;
            }
        }

        // Toggle subtitles
        function toggleSubtitles() {
            showSubtitles = !showSubtitles;
            const btn = document.getElementById('subtitlesBtn');
            
            if (showSubtitles) {
                btn.classList.add('active');
                btn.textContent = '💬 Subtitles: ON';
            } else {
                btn.classList.remove('active');
                btn.textContent = '💬 Subtitles: OFF';
                document.getElementById('subtitleOverlay').classList.remove('show');
            }
        }

        // Toggle voice
        function toggleVoice() {
            voiceEnabled = !voiceEnabled;
            const btn = document.getElementById('voiceBtn');
            
            if (voiceEnabled) {
                btn.classList.add('active');
                btn.textContent = '🔊 Voice: ON';
            } else {
                btn.classList.remove('active');
                btn.textContent = '🔊 Voice: OFF';
            }
        }

        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            stopCamera();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "model_loaded": detector is not None})

@app.route('/process_frame', methods=['POST'])
def process_frame():
    """Process single frame from browser camera - FAST VERSION"""
    try:
        # Quick validation
        if not detector:
            return jsonify({"success": False, "error": "Model not loaded"}), 500
        
        data = request.get_json(force=True)
        if not data or 'image' not in data:
            return jsonify({"success": False, "error": "No image data"}), 400
        
        # Decode base64 image (with timeout protection)
        try:
            image_data = data['image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({"success": False, "error": "Invalid image format"}), 400
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"success": False, "error": "Failed to decode image"}), 400
        
        # Resize frame for faster processing (smaller = faster)
        frame = cv2.resize(frame, (320, 240))
        
        # Process frame with detector
        label, confidence = detector.predict(frame)
        
        return jsonify({
            "success": True,
            "label": str(label),
            "confidence": float(confidence)
        })
        
    except Exception as e:
        print(f"❌ Frame processing error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": "Processing failed"}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🎉 PERFECT SIGN LANGUAGE DETECTION APP - BROWSER CAMERA")
    print("=" * 70)
    print("\n✨ Features:")
    print("   • Browser-based camera access (works on Render!)")
    print("   • Real-time detection via JavaScript")
    print("   • Beautiful modern UI")
    print("   • Live subtitles and statistics")
    print("\n📱 ACCESS FROM:")
    print("   • Local: http://localhost:5000")
    print("   • Render: Your Render app URL")
    print("\n💡 TIP: Allow camera access when browser asks!")
    print("=" * 70)
    print()
    
    # Get port from environment (Render uses PORT env variable)
    port = int(os.environ.get('PORT', 5000))
    print(f"   • Server running on port: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True, use_reloader=False)
